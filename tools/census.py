#!/usr/bin/env python3
"""The blind decode census: every byte of the cartridge, in both dialects.

Section 7 of tales-blockcodec-doc: **sweep per member, not per image**, and
"per member" has to mean per *container* member the moment the target has a
container.  `plausible()` bounds a candidate by whether its declared stream
fits inside the buffer it sits in, so inside a 64 KB member that rejects
nearly everything for free and inside a 256 MiB image it rejects almost
nothing.  A tool written for a flat file system fails silently on a nested
one, in the direction of a clean-looking negative.

This cartridge nests five deep and one of the levels is the *executable*:

    Nintendo DS ROM
      -> BLZ-packed module            32 of 33 modules, 1.6 MB -> 2.9 MB
      -> Nitro file system            5,114 named files, 31 overlays
        -> FPS4 archive               little-endian, and usually split into a
                                      `.b` index and a `.dat` payload, so the
                                      offsets in one file are into another
          -> FPS4 archive             members that are themselves archives
          -> V154                     the second container, which states its
                                      own length in two halves
        -> BIOS stream                LZ77 / LZ11 / RLE / Huffman / the two
                                      difference filters
        -> nine-byte block            decoded, and the plaintext descended into

**The BLZ level is the one that would have cost the result.**  The ARM9 and all
thirty-one overlays are packed; swept as shipped they are 1.6 MB of LZSS output
in which nothing parses, and the census would report a clean zero over code it
never read.  The modules are therefore swept in **plaintext**, and the packed
bytes they occupy on the cartridge are recorded as covered by them rather than
swept twice.

**The `.b` / `.dat` split is the one that would have cost the descent.**
Seventeen archives here are an index file whose entry offsets are into a
separate payload file.  Read on its own, `m.b` is a 67,008-byte file whose
1,521 members all run off its end -- which is an error, not a member list --
and `m.dat` is a 65 MB opaque blob.  Paired, they are 1,521 members.

The same split recurs **inside** the archives, and it has to be discovered
rather than assumed: `m.b` yields a member `AMUI00.B` which is itself an FPS4
whose offsets are into its sibling `AMUI00.MAPBIN`.  This tool pairs a member
whose name ends in `.B` with each sibling sharing its stem, in turn, and keeps
the first for which **every** entry lands inside the candidate -- so the
pairing is verified by the archive rather than by a naming rule that happens to
hold.  Anything still unreadable is counted and named in the output instead of
being skipped.

    python census.py IMAGE MODULEDIR --control PHANTASIA.sfc
    python census.py IMAGE MODULEDIR --part 0/8 --csv blocks-00.csv
    python census.py --merge DIR

`--part i/n` enumerates the same payload list and sweeps every n-th payload, so
the parts tile the cartridge exactly.  `--merge` reads a directory of part
outputs back and prints the totals, so the figure quoted in the documentation
is this tool's output rather than arithmetic done by hand.

Standard library only.
"""

import csv
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tales_block as tb
import fps4
import ndscomp
from ndsrom import NDS

MAX_DEPTH = 8
CAP = 24 << 20
OVERLAP = 12 << 20


# ------------------------------------------------------------------ the block

def is_block(buf):
    """(method, packed, unpacked) if buf is exactly one nine-byte block."""
    if len(buf) < 10:
        return None
    method = buf[0]
    if method not in (0, 1, 3):
        return None
    packed, unpacked = struct.unpack_from("<II", buf, 1)
    if packed + 9 != len(buf):
        return None
    if not 0 < unpacked <= 0x8000000:
        return None
    return method, packed, unpacked


def decode_block(buf):
    try:
        return tb.unpack(buf, 0, tb.PSX)
    except Exception:
        return None


# -------------------------------------------------------------- the containers

def fps4_members(buf, payload=None):
    """(archive, entries) if this is a readable FPS4, else None.

    `payload` is the separate `.dat` when the archive is an index file.  With
    no payload and members that run past the end of the index, this returns
    None rather than a truncated member list -- the failure the Xbox 360
    pipeline records as silent is made loud here.
    """
    if buf[:4] != b"FPS4":
        return None
    try:
        a = fps4.Fps4(bytes(buf), payload=payload)
    except Exception:
        return None
    if a.entry_size == 0 or a.count == 0 or a.count > 1 << 20:
        return None
    ents = a.entries()
    if not ents:
        return None
    n = len(a.payload)
    if any(e.offset + e.size > n for e in ents):
        return None
    return a, ents


def v154_regions(buf):
    """[(name, offset, size)] over a V154 object, or None.

    The header is 0x6C bytes.  `+0x14` and `+0x18` are two lengths whose sum is
    the object's own total length -- checked, and the walk is refused when it
    does not hold.  `+0x24` onwards is a run of (count, offset) pairs naming
    sub-tables, and the regions between consecutive offsets are yielded so that
    each gets its own plausibility bound.
    """
    if buf[:4] != b"V154" or len(buf) < 0x6C:
        return None
    a, b = struct.unpack_from("<II", buf, 0x14)
    total = a + b
    if total != len(buf):
        return None
    offs = []
    for i in range(0x24, 0x6C - 4, 8):
        cnt, off = struct.unpack_from("<II", buf, i)
        if 0 < off < len(buf) and cnt:
            offs.append(off)
    offs = sorted(set(offs))
    out = []
    prev = 0x6C
    for o in offs:
        if o <= prev:
            continue
        out.append(("region 0x%X" % prev, prev, o - prev))
        prev = o
    if prev < len(buf):
        out.append(("region 0x%X" % prev, prev, len(buf) - prev))
    return out


def bios_stream(buf):
    """(format name, plaintext) if the whole buffer is one BIOS stream.

    Only `LZ77` is falsifiable by decoding: it rejects a back-reference before
    the start of the output and its geometry caps the ratio at 8.47x.  `RLE`,
    the two difference filters and Huffman accept almost anything and `LZ11`
    has no useful ratio bound, so those are accepted only when the decode
    consumes the whole buffer exactly -- which is a weaker test and is labelled
    as one in the output.
    """
    if len(buf) < 8:
        return None
    t = buf[0]
    if t not in (0x10, 0x11, 0x24, 0x28, 0x30, 0x81, 0x82):
        return None
    try:
        plain, used = ndscomp.decompress(bytes(buf), 0)
    except Exception:
        return None
    if used != len(buf) or not plain:
        return None
    return ndscomp.TYPES.get(t, "0x%02X" % t), plain


# ------------------------------------------------------------------ enumerator

class Enumerator:
    """Yields (label, bytes) for every payload on the cartridge, exactly once."""

    def __init__(self, image, moddir, verbose=False):
        self.data = open(image, "rb").read()
        self.rom = NDS(self.data)
        self.moddir = moddir
        self.verbose = verbose
        self.n_fps4 = 0
        self.n_fps4_paired = 0
        self.n_v154 = 0
        self.n_bios = 0
        self.n_modules = 0
        self.blocks = []
        self.blocks_failed = []
        self.unreadable = []
        self.n_sidecar = 0
        self.bios_kinds = {}
        self.bios_packed = 0
        self.bios_plain = 0

    # -- containers ------------------------------------------------------

    def find_sibling(self, name, body, bodies):
        """The payload an `X.B` index belongs to, verified rather than guessed.

        Every sibling sharing the stem is tried in turn and the first for which
        every entry of the index lands inside it is kept.  Returning None means
        no sibling works, and the caller then records the archive as unreadable
        rather than reporting a truncated member list.
        """
        stem = name[:-2]
        cands = [v for k, v in bodies.items()
                 if k != name and k.upper().startswith(stem.upper())]
        cands.sort(key=len, reverse=True)
        for c in cands:
            if fps4_members(body, c):
                self.n_sidecar += 1
                return c
        return None

    def descend(self, label, buf, depth=0, payload=None):
        if depth >= MAX_DEPTH or len(buf) == 0:
            yield (label, buf)
            return

        got = fps4_members(buf, payload)
        if got:
            a, ents = got
            self.n_fps4 += 1
            if payload is not None:
                self.n_fps4_paired += 1
            first = min(e.offset for e in ents)
            table_end = a.table_off + a.count * a.entry_size
            yield ("%s [FPS4 header+table]" % label, buf[:min(table_end, len(buf))])
            covered = []
            bodies = {}
            for e in ents:
                if e.name:
                    bodies[e.name] = a.payload[e.offset:e.offset + e.size]
            for e in sorted(ents, key=lambda e: e.offset):
                covered.append((e.offset, e.offset + e.size))
                nm = e.name or "#%d" % e.index
                body = a.payload[e.offset:e.offset + e.size]
                sub = None
                if e.name and e.name.upper().endswith(".B"):
                    sub = self.find_sibling(e.name, body, bodies)
                for p in self.descend("%s/%s" % (label, nm), body,
                                      depth + 1, payload=sub):
                    yield p
            if payload is None:
                prev = max(first, min(table_end, len(buf)))
            else:
                prev = 0
            for lo, hi in sorted(covered):
                if lo > prev:
                    yield ("%s [slack 0x%X]" % (label, prev), a.payload[prev:lo])
                prev = max(prev, hi)
            if prev < len(a.payload):
                yield ("%s [slack 0x%X]" % (label, prev), a.payload[prev:])
            return

        if buf[:4] == b"FPS4":
            # An FPS4 whose members do not fit: say so rather than truncating.
            self.unreadable.append(label)

        regs = v154_regions(bytes(buf))
        if regs:
            self.n_v154 += 1
            yield ("%s [V154 header]" % label, buf[:0x6C])
            for nm, o, n in regs:
                for p in self.descend("%s/%s" % (label, nm), buf[o:o + n],
                                      depth + 1):
                    yield p
            return

        got = bios_stream(buf)
        if got:
            name, plain = got
            self.n_bios += 1
            self.bios_kinds[name] = self.bios_kinds.get(name, 0) + 1
            self.bios_packed += len(buf)
            self.bios_plain += len(plain)
            yield ("%s [%s header]" % (label, name), buf[:4])
            for p in self.descend("%s <%s>" % (label, name), plain, depth + 1):
                yield p
            return

        b = is_block(buf)
        if b:
            plain = decode_block(bytes(buf))
            if plain is not None and len(plain) == b[2]:
                self.blocks.append((label, b[0], b[1], b[2]))
                yield ("%s [block header]" % label, buf[:9])
                for p in self.descend("%s <block m%d>" % (label, b[0]), plain,
                                      depth + 1):
                    yield p
                return
            self.blocks_failed.append((label, b[0], b[1], b[2]))

        yield (label, buf)

    # -- the cartridge ---------------------------------------------------

    def payloads(self):
        d = self.data
        h = self.rom.hdr
        fat = self.rom.fat()
        files, _ = self.rom.fnt()
        by_path = {p: fid for fid, p in files}
        ov_ids = set()
        for cpu in (9, 7):
            for o in self.rom.overlays(cpu):
                ov_ids.add(o["file_id"])

        # 1. the header and the tables, each as its own payload
        yield ("[ROM header 0x0]", d[:0x200])
        yield ("[header slack 0x200]", d[0x200:h["arm9_rom_off"]])

        # 2. the executable modules, in plaintext
        covered = [(0, h["arm9_rom_off"])]
        for name in sorted(os.listdir(self.moddir)):
            if not name.endswith(".bin"):
                continue
            self.n_modules += 1
            buf = open(os.path.join(self.moddir, name), "rb").read()
            for p in self.descend("[module %s, BLZ plaintext]" % name[:-4], buf):
                yield p
        covered.append((h["arm9_rom_off"], h["arm9_rom_off"] + h["arm9_size"]))
        covered.append((h["arm7_rom_off"], h["arm7_rom_off"] + h["arm7_size"]))
        for fid in ov_ids:
            covered.append(fat[fid])

        # 3. the tables
        for nm, off, size in (("FNT", h["fnt_off"], h["fnt_size"]),
                              ("FAT", h["fat_off"], h["fat_size"]),
                              ("overlay table 9", h["arm9_ovt_off"], h["arm9_ovt_size"]),
                              ("banner", h["banner_off"], 0xA00)):
            if off and size:
                yield ("[%s]" % nm, d[off:off + size])
                covered.append((off, off + size))

        # 4. the files, with `.b` / `.dat` pairs read together
        paired_dat = set()
        for fid, p in files:
            if p.endswith(".b"):
                partner = p[:-2] + ".dat"
                if partner in by_path:
                    paired_dat.add(by_path[partner])

        for fid, p in sorted(files, key=lambda x: fat[x[0]][0]):
            if fid in ov_ids:
                continue
            s, e = fat[fid]
            covered.append((s, e))
            if fid in paired_dat:
                continue                       # swept through its index
            payload = None
            if p.endswith(".b"):
                partner = p[:-2] + ".dat"
                if partner in by_path:
                    ps, pe = fat[by_path[partner]]
                    payload = d[ps:pe]
            for q in self.descend(p, d[s:e], payload=payload):
                yield q

        # 5. the complement: every stretch no payload above covers
        covered.sort()
        prev = 0
        for lo, hi in covered:
            if lo > prev:
                yield ("[gap 0x%X]" % prev, d[prev:lo])
            prev = max(prev, hi)
        if prev < len(d):
            yield ("[tail 0x%X]" % prev, d[prev:])


def payloads(image, moddir):
    """Module-level shortcut, so the other tools share this descent.

    `internal_names.py`, `formats.py`, `media_census.py`, `crosstitle.py` and
    `deflate_control.py` all have to see the same payload list the census sees,
    or their denominators disagree with it and the cartridge appears to be two
    different cartridges.
    """
    en = Enumerator(image, moddir)
    for p in en.payloads():
        yield p


# ------------------------------------------------------------------ the sweep

def windows(buf, cap, overlap):
    if len(buf) <= cap:
        yield 0, buf
        return
    step = cap - overlap
    i = 0
    while i < len(buf):
        yield i, buf[i:i + cap]
        if i + cap >= len(buf):
            break
        i += step


def sweep(label, buf, out, split_log):
    """Every offset in one payload, both dialects, recording every survivor."""
    n = 0
    for base, w in windows(buf, CAP, OVERLAP):
        if base:
            split_log.append(label)
        for dialect, dname in ((tb.PSX, "psx"), (tb.SNES, "snes")):
            for off, packed, unpacked in tb.scan(w, dialect):
                out.append((label, dname, base + off, packed, unpacked))
                n += 1
    return n


def main(argv):
    if "--merge" in argv:
        return merge(argv[argv.index("--merge") + 1])
    if len(argv) < 3:
        print(__doc__)
        return 2
    image, moddir = argv[1], argv[2]
    part = (0, 1)
    if "--part" in argv:
        i, n = argv[argv.index("--part") + 1].split("/")
        part = (int(i), int(n))
    csv_path = argv[argv.index("--csv") + 1] if "--csv" in argv else None
    control = argv[argv.index("--control") + 1] if "--control" in argv else None

    en = Enumerator(image, moddir)
    hits = []
    split_log = []
    n_payloads = 0
    n_bytes = 0
    swept = 0
    swept_bytes = 0
    print("census of %s with plaintext modules from %s" % (image, moddir))
    print("part %d of %d" % (part[0], part[1]))
    print("")
    for i, (label, buf) in enumerate(en.payloads()):
        n_payloads += 1
        n_bytes += len(buf)
        if i % part[1] != part[0]:
            continue
        swept += 1
        swept_bytes += len(buf)
        sweep(label, buf, hits, split_log)

    print("containers descended into")
    print("  BLZ-packed modules, swept in plaintext : %d" % en.n_modules)
    print("  FPS4 archives                          : %d" % en.n_fps4)
    print("      of which paired with a `.dat` file     : %d" % en.n_fps4_paired)
    print("      of which paired with a sibling member  : %d" % en.n_sidecar)
    print("  V154 objects                           : %d" % en.n_v154)
    print("  BIOS-format streams                    : %d, %d -> %d bytes (%.2fx)"
          % (en.n_bios, en.bios_packed, en.bios_plain,
             en.bios_plain / en.bios_packed if en.bios_packed else 0))
    for k in sorted(en.bios_kinds):
        print("      %-10s %d" % (k, en.bios_kinds[k]))
    print("      Only LZ77 is falsifiable by decoding; the rest are counted")
    print("      because the decode consumed the whole payload exactly, which")
    print("      is a weaker test, and section 7 requires saying so.")
    print("  FPS4 archives that could NOT be read   : %d" % len(en.unreadable))
    for u in en.unreadable[:20]:
        print("      %s" % u)
    print("")
    print("payloads enumerated : %d, %d bytes" % (n_payloads, n_bytes))
    print("payloads swept      : %d, %d bytes" % (swept, swept_bytes))
    if split_log:
        print("payloads swept in overlapping windows (%d MiB, %d MiB overlap):"
              % (CAP >> 20, OVERLAP >> 20))
        for s in sorted(set(split_log)):
            print("      %s" % s)
    print("")

    print("the structural census -- payloads that ARE a nine-byte block")
    print("  decoded to their declared length : %d" % len(en.blocks))
    print("  right header, wrong length       : %d" % len(en.blocks_failed))
    for b in en.blocks_failed[:20]:
        print("      %s  method %d packed %d unpacked %d" % b)
    print("")

    print("the blind sweep -- every offset of every payload, both dialects")
    print("  survivors : %d" % len(hits))
    for hrow in hits[:60]:
        print("      %s  %s +%d  packed %d -> %d" % hrow)
    print("")

    if control:
        cb = open(control, "rb").read()
        cn = 0
        for dialect in (tb.SNES,):
            cn += len(list(tb.scan(cb, dialect)))
        print("control: %s" % os.path.basename(control))
        print("  blocks found by the same unmodified decoder in this run : %d" % cn)
        print("  (the 1995 cartridge returns 1,089; a census that cannot")
        print("   find those is not evidence about anything)")

    if csv_path:
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["label", "dialect", "offset", "packed", "unpacked"])
            for r in hits:
                w.writerow(r)
        print("")
        print("wrote %s" % csv_path)
    return 0


def merge(dirname):
    tot = 0
    parts = 0
    for n in sorted(os.listdir(dirname)):
        if not n.endswith(".csv"):
            continue
        parts += 1
        with open(os.path.join(dirname, n), newline="") as f:
            tot += sum(1 for _ in csv.reader(f)) - 1
    print("%d part files, %d survivors in total" % (parts, tot))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
