#!/usr/bin/env python3
"""Does this cartridge hold compressed data?  Asked without any probe at all.

The counter-check that depends on nothing: run the medium through
`zlib.compress` and see how much comes off.  On *Tales of the Tempest* the raw
cartridge deflated to 52.6% and that was consistent with the data being stored
plain; on *Tales of Innocence* it deflated to 73.5%, and the number that
settled the question was not the total but **the split** -- 91.27% for the
already-compressed containers against 52.23% for everything else.

So this tool reports by class, and the classes come from `formats.py`, which
classifies by magic and never by extension.  The total is printed last and is
the least interesting line in the table.

**On this cartridge the classes have to include the executable, and that is
new.**  Thirty-two of the thirty-three modules are `BLZ`-packed, so the code
appears twice: once as shipped, where it is already compressed and will not
deflate, and once in plaintext, where it will.  Both are reported, because the
difference between them is the only measurement of what the linker's own
compressor achieved.

    python deflate_control.py IMAGE MODULEDIR
    python deflate_control.py IMAGE MODULEDIR --sample 4194304

Standard library only.
"""

import collections
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formats
from ndsrom import NDS


def ratio(buf, sample=None):
    if sample and len(buf) > sample:
        buf = buf[:sample]
    if not buf:
        return None, 0
    return len(zlib.compress(bytes(buf), 6)) / float(len(buf)), len(buf)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    image, moddir = argv[1], argv[2]
    sample = int(argv[argv.index("--sample") + 1]) if "--sample" in argv else None
    data = open(image, "rb").read()
    rom = NDS(data)
    fat = rom.fat()
    files, _ = rom.fnt()
    by_id = dict(files)
    ov = set()
    for cpu in (9, 7):
        for o in rom.overlays(cpu):
            ov.add(o["file_id"])

    classes = collections.defaultdict(lambda: [0, 0, 0])   # count, raw, deflated

    def add(cls, buf):
        if not buf:
            return
        b = bytes(buf[:sample]) if sample and len(buf) > sample else bytes(buf)
        classes[cls][0] += 1
        classes[cls][1] += len(b)
        classes[cls][2] += len(zlib.compress(b, 6))

    for fid, (s, e) in enumerate(fat):
        buf = data[s:e]
        if fid in ov:
            add("executable, BLZ-packed as shipped", buf)
            continue
        p = by_id.get(fid, "")
        kind, what = formats.classify(buf)
        if p.endswith(".sdat"):
            add("sound archive (SDAT)", buf)
        elif p.startswith("/movie/"):
            add("video (Mobiclip)", buf)
        elif kind == "audio":
            add("voice (CRI AHX)", buf)
        elif kind == "container":
            add("container (FPS4 / V154)", buf)
        elif kind == "compressed":
            add("BIOS-format stream", buf)
        else:
            add("everything else", buf)

    add("executable, BLZ-packed as shipped",
        data[rom.hdr["arm9_rom_off"]:rom.hdr["arm9_rom_off"] + rom.hdr["arm9_size"]])
    add("executable, ARM7 (not packed)",
        data[rom.hdr["arm7_rom_off"]:rom.hdr["arm7_rom_off"] + rom.hdr["arm7_size"]])
    for n in sorted(os.listdir(moddir)):
        if n.endswith(".bin"):
            add("executable, BLZ plaintext", open(os.path.join(moddir, n), "rb").read())

    tail_start = max(e for _, e in fat)
    add("the unused tail", data[tail_start:])

    print("deflate control on %s" % os.path.basename(image))
    if sample:
        print("(each payload sampled to its first %d bytes)" % sample)
    print("")
    print("%-38s %7s %14s %14s %8s"
          % ("class", "count", "bytes", "deflated", "ratio"))
    for cls in sorted(classes, key=lambda c: -classes[c][1]):
        c, raw, defl = classes[cls]
        print("%-38s %7d %14d %14d %7.2f%%"
              % (cls, c, raw, defl, 100.0 * defl / raw if raw else 0))
    traw = sum(v[1] for v in classes.values())
    tdef = sum(v[2] for v in classes.values())
    print("%-38s %7d %14d %14d %7.2f%%"
          % ("TOTAL", sum(v[0] for v in classes.values()), traw, tdef,
             100.0 * tdef / traw if traw else 0))
    print("")
    whole, n = ratio(data, sample)
    print("the whole image as one buffer: %d bytes -> %.2f%%" % (n, 100.0 * whole))
    print("")
    print("for comparison, the same measurement on other builds:")
    print("  Tales of the Tempest, DS 2006     52.6%  (data stored raw)")
    print("  Tales of Innocence,   DS 2007     73.5%  -- 91.27% for its")
    print("                                    containers, 52.23% for the rest")
    print("  Ratatosk no Kishi,    Wii 2008    89.62% / 50.74%")
    print("  Tales of Vesperia,    X360 2008   99.20% / 33.19%")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
