#!/usr/bin/env python3
"""Classify every payload on the cartridge, and account for every byte of it.

Classification is by **magic and arithmetic, never by extension**.  On these
cartridges that distinction does real work: 63 files are named `.dat` and they
are at least five different things -- an `FPS4` archive, a `V154` object, a
BIOS `LZ11` stream, a plain table and a container payload whose index lives in
a `.b` file beside it -- while `.b` and `.dat` are one archive in two files
rather than two formats, and `.ds3` is not a format at all but this project's
own extension, `V154` inside.

Three passes, because the cartridge has three levels and folding them together
would turn measurements into estimates:

  * **pass 1** -- the 5,145 files as the Nitro file system stores them;
  * **pass 2** -- the members inside every container, including the archives
    nested inside other archives, from the same enumerator the census uses;
  * **pass 3** -- what those payloads are once **decompressed**: a `BLZ`-packed
    module at its plaintext length, a BIOS stream at its decoded length, so the
    third table says what the machine actually holds rather than what the
    cartridge stores.

`--budget` is the separate question: how was every byte of the 256 MiB spent.
It tessellates the image -- header, tables, modules, files, alignment slack,
tail -- and **checks that the pieces sum to the image**, printing the
discrepancy rather than trusting the arithmetic.  It also reports **what the
unused space is made of**, because on *Tales of Vesperia* a 19.08% region that
looked empty turned out to be incompressible pseudo-random fill and was not
free space at all.

    python formats.py IMAGE MODULEDIR
    python formats.py IMAGE MODULEDIR --budget
    python formats.py IMAGE MODULEDIR --csv per-payload.csv

Standard library only.
"""

import collections
import csv as csvmod
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census
import ndscomp
from ndsrom import NDS

MAGIC = [
    (b"FPS4", "container", "the studio's own archive, little-endian here"),
    (b"V154", "container", "the studio's second container"),
    (b"MODS", "video", "Actimagine Mobiclip"),
    (b"SDAT", "audio", "NitroSDK sound archive"),
    (b"RTFN", "font", "NitroSDK font (NFTR, tag reversed)"),
    (b"RGCN", "graphics", "NitroSDK character graphics (NCGR)"),
    (b"RLCN", "graphics", "NitroSDK palette (NCLR)"),
    (b"RCSN", "graphics", "NitroSDK screen (NSCR)"),
    (b"RECN", "graphics", "NitroSDK cell bank (NCER)"),
    (b"RNAN", "graphics", "NitroSDK animation (NANR)"),
    (b"BMD0", "model", "NitroSDK model (NSBMD)"),
    (b"BCA0", "model", "NitroSDK animation (NSBCA)"),
    (b"BTX0", "model", "NitroSDK texture (NSBTX)"),
    (b"SWAV", "audio", "NitroSDK wave"),
    (b"SBNK", "audio", "NitroSDK bank"),
    (b"SSEQ", "audio", "NitroSDK sequence"),
    (b"STRM", "audio", "NitroSDK stream"),
]

# CRI ADX and AHX both open 0x80 0x00; the encoding byte at +4 tells them apart
# and the copyright string near the end of the header confirms both.
ADX_TYPES = {0x02: "ADX (CRI, 4-bit ADPCM)", 0x03: "ADX (CRI, 4-bit ADPCM)",
             0x10: "AHX (CRI, MPEG-2 audio)", 0x11: "AHX (CRI, MPEG-2 audio)"}

KIND_OF = {
    "container": "container", "video": "media", "audio": "media",
    "font": "font", "graphics": "graphics", "model": "model",
    "code": "code", "compressed": "compressed", "table": "table",
    "unknown": "unknown", "empty": "empty",
}


def classify(buf):
    """(kind, what) from the bytes alone."""
    if not buf:
        return "empty", "zero bytes"
    for m, kind, what in MAGIC:
        if buf[:len(m)] == m:
            return kind, what
    if buf[:2] == b"\x80\x00" and len(buf) > 6:
        t = buf[4]
        if t in ADX_TYPES:
            return "audio", ADX_TYPES[t]
        return "audio", "CRI ADX-family header, encoding 0x%02X" % t
    if buf[0] in (0x10, 0x11, 0x24, 0x28, 0x30, 0x81, 0x82) and len(buf) >= 8:
        size = buf[1] | (buf[2] << 8) | (buf[3] << 16)
        if size:
            return "compressed", "BIOS %s stream" % ndscomp.TYPES.get(
                buf[0], "0x%02X" % buf[0])
    if len(buf) >= 4 and buf[:4] in (b"\x00\x00\x00\x00",):
        pass
    # A run of one byte value is fill, whatever it is a fill of.
    if len(buf) >= 16 and len(set(buf[:4096])) == 1:
        return "fill", "a single byte value, 0x%02X" % buf[0]
    return "unknown", "unclassified"


def table(rows, total, title):
    print(title)
    print("  %-12s %8s %14s %8s  %s"
          % ("kind", "count", "bytes", "share", "what"))
    agg = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for kind, what, n in rows:
        a = agg[kind]
        a[0] += 1
        a[1] += n
        a[2][what] += 1
    for kind, (c, n, whats) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        top = ", ".join("%s x%d" % (w, k) for w, k in whats.most_common(2))
        print("  %-12s %8d %14d %7.2f%%  %s"
              % (kind, c, n, 100.0 * n / total if total else 0, top[:60]))
    print("  %-12s %8d %14d %7.2f%%"
          % ("TOTAL", len(rows), sum(r[2] for r in rows),
             100.0 * sum(r[2] for r in rows) / total if total else 0))
    print("")


def budget(image, moddir):
    """Every byte of the cartridge, tessellated and checked."""
    data = open(image, "rb").read()
    rom = NDS(data)
    h = rom.hdr
    fat = rom.fat()
    files, _ = rom.fnt()
    by_id = dict(files)
    ov = set()
    for cpu in (9, 7):
        for o in rom.overlays(cpu):
            ov.add(o["file_id"])

    pieces = []
    pieces.append(("cartridge header", 0, h["arm9_rom_off"]))
    pieces.append(("ARM9, BLZ-packed", h["arm9_rom_off"],
                   h["arm9_rom_off"] + h["arm9_size"]))
    pieces.append(("ARM7", h["arm7_rom_off"], h["arm7_rom_off"] + h["arm7_size"]))
    pieces.append(("overlay table", h["arm9_ovt_off"],
                   h["arm9_ovt_off"] + h["arm9_ovt_size"]))
    pieces.append(("file name table", h["fnt_off"], h["fnt_off"] + h["fnt_size"]))
    pieces.append(("file allocation table", h["fat_off"],
                   h["fat_off"] + h["fat_size"]))
    pieces.append(("banner", h["banner_off"], h["banner_off"] + 0xA00))

    by_kind = collections.Counter()
    for fid, (s, e) in enumerate(fat):
        if fid in ov:
            pieces.append(("overlays, BLZ-packed (%d of them)" % len(ov), s, e))
            continue
        p = by_id.get(fid, "<unnamed %d>" % fid)
        kind, what = classify(data[s:e])
        if p.endswith(".sdat"):
            kind = "music and effects"
        elif p.startswith("/movie/"):
            kind = "video"
        elif p.startswith("/s/") and not p.startswith("/s/lvd"):
            kind = "voice"
        pieces.append(("file:%s" % kind, s, e))

    pieces.sort(key=lambda x: x[1])
    agg = collections.Counter()
    counts = collections.Counter()
    prev = 0
    slack = 0
    slack_bytes = collections.Counter()
    for name, s, e in pieces:
        if s > prev:
            slack += s - prev
            for b in data[prev:s][:1 << 20]:
                slack_bytes[b] += 1
        agg[name.split(":", 1)[-1] if name.startswith("file:") else name] += e - s
        counts[name.split(":", 1)[-1] if name.startswith("file:") else name] += 1
        prev = max(prev, e)
    tail = len(data) - prev
    tail_bytes = collections.Counter(data[prev:prev + (4 << 20)])

    n = len(data)
    print("the budget: every byte of %s, %d bytes" % (os.path.basename(image), n))
    print("")
    print("  %-28s %8s %14s %8s" % ("what", "count", "bytes", "share"))
    tot = 0
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]):
        print("  %-28s %8d %14d %7.2f%%" % (k, counts[k], v, 100.0 * v / n))
        tot += v
    print("  %-28s %8s %14d %7.2f%%" % ("alignment slack between them", "", slack,
                                        100.0 * slack / n))
    print("  %-28s %8s %14d %7.2f%%" % ("tail after the last file", "", tail,
                                        100.0 * tail / n))
    print("")
    print("  %-28s %8s %14d %7.2f%%" % ("sum of the pieces", "", tot + slack + tail,
                                        100.0 * (tot + slack + tail) / n))
    print("  %-28s %8s %14d" % ("image size", "", n))
    print("  %-28s %8s %14d   <- must be zero"
          % ("discrepancy", "", n - (tot + slack + tail)))
    print("")
    print("what the unused space is made of")
    print("  alignment slack, first 1 MiB sampled: %d distinct byte values"
          % len(slack_bytes))
    for b, c in slack_bytes.most_common(4):
        print("      0x%02X  %d" % (b, c))
    print("  tail, first 4 MiB sampled: %d distinct byte values" % len(tail_bytes))
    for b, c in tail_bytes.most_common(4):
        print("      0x%02X  %d" % (b, c))
    if tail:
        comp = len(zlib.compress(data[prev:prev + (4 << 20)], 6))
        print("  the tail deflates to %.4f%% of itself -- fill this compressible"
              % (100.0 * comp / min(tail, 4 << 20)))
        print("  is free space; incompressible fill would not be.")
    return 0


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    image, moddir = argv[1], argv[2]
    if "--budget" in argv:
        return budget(image, moddir)

    data = open(image, "rb").read()
    rom = NDS(data)
    fat = rom.fat()
    files, _ = rom.fnt()
    n = len(data)

    print("pass 1 -- the %d files as the Nitro file system stores them" % len(fat))
    rows = []
    for fid, (s, e) in enumerate(fat):
        kind, what = classify(data[s:e])
        rows.append((kind, what, e - s))
    table(rows, n, "")

    print("pass 2 -- every payload the census enumerates, containers descended")
    en = census.Enumerator(image, moddir)
    rows2 = []
    total2 = 0
    for label, buf in en.payloads():
        kind, what = classify(bytes(buf[:64]) if len(buf) > 64 else bytes(buf))
        if len(buf) == 0:
            continue
        rows2.append((kind, what, len(buf)))
        total2 += len(buf)
    table(rows2, total2, "")
    print("  containers descended: %d FPS4 (%d paired with a .dat, %d with a"
          " sibling member), %d V154, %d BIOS streams, %d BLZ modules"
          % (en.n_fps4, en.n_fps4_paired, en.n_sidecar, en.n_v154, en.n_bios,
             en.n_modules))
    print("  %d bytes of payload against %d bytes of cartridge -- the excess is"
          % (total2, n))
    print("  what decompression adds, which is the point of pass 3.")
    print("")

    print("pass 3 -- what the cartridge holds once every stream is expanded")
    print("  BLZ modules   : %d bytes packed -> %d bytes of code"
          % (sum(fat[o["file_id"]][1] - fat[o["file_id"]][0]
                 for cpu in (9, 7) for o in rom.overlays(cpu))
             + rom.hdr["arm9_size"] + rom.hdr["arm7_size"],
             sum(os.path.getsize(os.path.join(moddir, f))
                 for f in os.listdir(moddir) if f.endswith(".bin"))))
    packed = expanded = 0
    nstreams = 0
    for fid, (s, e) in enumerate(fat):
        buf = data[s:e]
        got = census.bios_stream(buf)
        if got:
            nstreams += 1
            packed += len(buf)
            expanded += len(got[1])
    print("  BIOS streams  : %d whole files, %d bytes -> %d bytes"
          % (nstreams, packed, expanded))
    if "--csv" in argv:
        path = argv[argv.index("--csv") + 1]
        with open(path, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(["kind", "what", "bytes"])
            for r in rows2:
                w.writerow(r)
        print("")
        print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
