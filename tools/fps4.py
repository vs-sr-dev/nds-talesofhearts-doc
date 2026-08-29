#!/usr/bin/env python3
"""
fps4.py -- reader for FPS4, the container used by this studio line in 2008.

It was first read on the Xbox 360 *Tales of Vesperia* disc, where every `.svo`
and `lib_data/syspack.dat` is an FPS4 archive and every word in the header is
**big-endian**.  It is on the *Tales of Hearts* Nintendo DS cartridges four
months later with the same field layout and the same field-mask semantics, and
there it is **little-endian** -- so the byte order is the machine's and the
structure is the line's.  This reader decides the byte order from the archive
in hand rather than from a constant.

The test is the entry size at +0x10, a `u16` that is 0x2C or 0x04 on every
archive seen: read the wrong way round those are 0x2C00 and 0x0400, so one
reading is plausible and the other is not.  The entry-table offset at +0x08 is
0x1C on every archive and agrees.

Header (0x1C bytes)
-------------------------------
    0x00  4  magic "FPS4"
    0x04  4  entry count, including a terminating entry with a zero size
    0x08  4  offset of the entry table (0x1C on every archive here)
    0x0C  4  offset of the first payload
    0x10  2  entry size in bytes (0x2C on every archive here)
    0x12  2  field mask -- which of the per-entry fields are present (0x000F)
    0x14  4  unknown, 0x00010000 on the Xbox 360 archives
    0x18  4  offset of the trailing build-path string, 0 when there is none

Entry (0x2C bytes on most archives)
-----------------------------------
The entry layout is not fixed: the header's field mask says which fields are
present, and they are stored in bit order.  Bit 0 is the payload offset, bit 1
the offset padded to the archive's alignment, bit 2 the exact size, bit 3 a
32-byte NUL-padded ASCII name.  Two masks occur on this disc:

    0x000F   offset, padded size, exact size, name   -- every `.svo`, and
                                                       most DS archives
    0x008D   offset, exact size, name                -- `lib_data/syspack.dat`
    0x0003   offset and padded size, 8-byte entries  -- the DS icon indexes
    0x0001   offset only, 4-byte entries             -- the archives nested
                                                       inside those

**A mask with no size field in it does not mean the sizes are missing.**  On
mask 0x0001 each member runs from its own offset to the next entry's, and the
last entry is a terminator whose offset is the archive's length -- the same
convention the 0x000F archives use for their final entry.  A reader that
requires an explicit size finds no members at all and reports the archive as
unreadable, which is how 1,904 nested archives on the *Tales of Hearts*
cartridges were nearly written off.  That is the field-mask trap of the Xbox
360 pipeline in its other direction: there a missing field was read as a
present one, here a present field was read as missing.

so a reader that assumes one layout misreads the other silently, in the
direction of enormous sizes rather than of an error.  `syspack.dat` is an
index into `syspack.dav` beside it, which is why one of its three members has
offset 0 and the size of that whole file.

The last entry of a 0x000F archive has a zero exact size and no name; it marks
the end of the payload area, so its offset is the archive's total length.

The trailing string is a build path -- `../Release/<dir>/<name>.svo` -- whose
middle component is Shift-JIS, so it is reported as raw bytes as well as
decoded.

On the Nintendo DS the directory is often a **separate file**: `m.b` carries
1,522 entries and no payload of its own, and its offsets are into `m.dat`
beside it.  Pass the payload with `--payload` to read such a pair; without it
every member runs off the end of the index, which this reader reports rather
than silently truncating.

    python fps4.py list    FILE [--payload FILE]
    python fps4.py info    FILE [FILE ...]
    python fps4.py extract FILE OUTDIR [--payload FILE]
"""

import os
import struct
import sys

MAGIC = b"FPS4"
HDR = 0x1C


class Entry:
    __slots__ = ("index", "offset", "padded", "size", "name")

    def __init__(self, index, offset, padded, size, name):
        self.index, self.offset, self.padded = index, offset, padded
        self.size, self.name = size, name


def detect_endian(data):
    """Which way round this archive's header words are, read off the header.

    Returns '>' or '<'.  The entry size at +0x10 is a u16 that is small on
    every archive in either corpus; read the wrong way round it is at least
    0x0400.  The entry-table offset at +0x08 is 0x1C and agrees.
    """
    votes = {'>': 0, '<': 0}
    for e in ('>', '<'):
        esz = struct.unpack_from(e + 'H', data, 0x10)[0]
        if 4 <= esz <= 0x100:
            votes[e] += 1
        if struct.unpack_from(e + 'I', data, 8)[0] == HDR:
            votes[e] += 1
        cnt = struct.unpack_from(e + 'I', data, 4)[0]
        if 0 < cnt < 1 << 20:
            votes[e] += 1
    return '>' if votes['>'] > votes['<'] else '<'


class Fps4:
    def __init__(self, data, origin="", payload=None, endian=None):
        if data[:4] != MAGIC:
            raise ValueError("not an FPS4 archive")
        self.data = data
        self.payload = payload if payload is not None else data
        self.origin = origin
        self.endian = endian or detect_endian(data)
        e = self.endian
        (self.count, self.table_off, self.data_off) = struct.unpack_from(e + "III", data, 4)
        (self.entry_size, self.field_mask) = struct.unpack_from(e + "HH", data, 0x10)
        (self.unknown, self.string_off) = struct.unpack_from(e + "II", data, 0x14)

    def build_path(self):
        """The trailing build path as (raw bytes, best-effort text)."""
        if not self.string_off or self.string_off >= len(self.data):
            return b"", ""
        end = self.data.find(b"\0", self.string_off)
        raw = self.data[self.string_off:end if end >= 0 else len(self.data)]
        try:
            text = raw.decode("shift_jis")
        except UnicodeDecodeError:
            text = raw.decode("latin1")
        return raw, text

    def entries(self):
        """Members, decoded according to the header field mask."""
        m = self.field_mask
        out = []
        raw = []
        for i in range(self.count):
            o = self.table_off + i * self.entry_size
            if o + self.entry_size > len(self.data):
                break
            c = o
            off = padded = size = None
            name = ""
            if m & 0x01:
                off = struct.unpack_from(self.endian + "I", self.data, c)[0]
                c += 4
            if m & 0x02:
                padded = struct.unpack_from(self.endian + "I", self.data, c)[0]
                c += 4
            if m & 0x04:
                size = struct.unpack_from(self.endian + "I", self.data, c)[0]
                c += 4
            if m & 0x08:
                name = self.data[c:c + 32].split(bytes(1))[0].decode("latin1")
                c += 32
            if off is None:
                continue
            if size is None:
                size = padded
            if padded is None:
                padded = size
            if size is None:
                # No size field in the mask at all: the member runs to the
                # next entry's offset, and the last entry is a terminator.
                raw.append((i, off, name))
                continue
            if size == 0 and not name:
                continue                      # the terminator, not a member
            out.append(Entry(i, off, padded, size, name))
        if raw:
            raw.sort(key=lambda r: r[1])
            end = len(self.payload)
            for k, (i, off, name) in enumerate(raw):
                nxt = raw[k + 1][1] if k + 1 < len(raw) else end
                if nxt <= off:
                    continue
                out.append(Entry(i, off, nxt - off, nxt - off, name))
        return out

    def implicit_sizes(self):
        """True when this archive states no size and sizes come from offsets."""
        return not (self.field_mask & 0x06)

    def read(self, e):
        return self.payload[e.offset:e.offset + e.size]

    def truncated(self):
        """Members that run past the end of the payload -- the sidecar check."""
        return [e for e in self.entries()
                if e.offset + e.size > len(self.payload)]


def load(path, payload_path=None):
    with open(path, "rb") as f:
        data = f.read()
    pay = None
    if payload_path:
        with open(payload_path, "rb") as f:
            pay = f.read()
    return Fps4(data, os.path.basename(path), pay)


def cmd_info(args):
    for path in args.files:
        a = load(path)
        raw, text = a.build_path()
        ents = a.entries()
        total = sum(e.size for e in ents)
        print("%s" % os.path.basename(path))
        print("  entries       : %d table (%d members + terminator)" % (a.count, len(ents)))
        print("  byte order    : %s" % ("big-endian" if a.endian == ">" else "little-endian"))
        print("  entry size    : 0x%02X   field mask 0x%04X   word 0x%08X"
              % (a.entry_size, a.field_mask, a.unknown))
        print("  table at      : 0x%X      first payload at 0x%X" % (a.table_off, a.data_off))
        print("  member bytes  : %d of %d on disc (%.2f%%)"
              % (total, len(a.data), 100.0 * total / len(a.data) if a.data else 0))
        print("  build path    : %s" % text)
        print("  build path raw: %s" % raw.hex())
    return 0


def cmd_list(args):
    a = load(args.file, getattr(args, "payload", None))
    bad = a.truncated()
    if bad:
        print("# %d of %d members run past the end of the payload (%d bytes)."
              % (len(bad), len(a.entries()), len(a.payload)))
        print("# This archive is an index: pass the payload file with --payload.")
    print("%-5s %12s %12s %12s  %s" % ("#", "offset", "padded", "size", "name"))
    for e in a.entries():
        print("%-5d %12d %12d %12d  %s" % (e.index, e.offset, e.padded, e.size, e.name))
    return 0


def cmd_extract(args):
    a = load(args.file, getattr(args, "payload", None))
    os.makedirs(args.outdir, exist_ok=True)
    n = 0
    for e in a.entries():
        if not e.name:
            continue
        with open(os.path.join(args.outdir, e.name), "wb") as f:
            f.write(a.read(e))
        n += 1
    print("extracted %d members to %s" % (n, args.outdir))
    return 0


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Reader for the FPS4 container.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("info"); s.add_argument("files", nargs="+"); s.set_defaults(func=cmd_info)
    s = sub.add_parser("list"); s.add_argument("file")
    s.add_argument("--payload"); s.set_defaults(func=cmd_list)
    s = sub.add_parser("extract"); s.add_argument("file"); s.add_argument("outdir")
    s.add_argument("--payload"); s.set_defaults(func=cmd_extract)
    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
