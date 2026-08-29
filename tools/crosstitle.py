"""This cartridge against its neighbours, and against its own other edition.

Three comparisons are available here and the first of them is new to the
corpus: *Tales of Hearts* shipped as **two cartridges** on one day, an Anime
Movie Edition and a CG Movie Edition, and everything identical between them is
the game while everything that differs is the edition.  That is a control the
corpus has never had on a cartridge, and it is free.

The other two are the ones the corpus has been asking for:

  * *Tales of Innocence* (2007) and *Tales of the Tempest* (2006), the same
    machine and the same instruction set, one and two years earlier, from two
    studios outside the line -- the perfect negative controls, and this is the
    first time in the corpus that a same-ISA control was available for a DS
    result;
  * *Tales of Vesperia* (Xbox 360), whose executable is stamped five months
    before this one and which carries the project tag `TO8` where this
    cartridge carries `TO9`.

Four ways, each reported separately:

  1. **whole payloads, by SHA-1** -- an asset carried across unchanged shows up
     here and nowhere else.  This cartridge's payloads are container *members*,
     not files, so a comparison at file level would compare 75 archives against
     several thousand files and report a meaningless zero;
  2. **names**, case-folded, basename only -- a re-encoded asset keeps its name
     when its bytes change, which is how the 109 `tor_` leftovers on the
     *Abyss* disc were found;
  3. **the compressor's preamble** -- the first sixteen bytes of every
     compressed payload, tabulated position by position.  On the 2003 GameCube
     and 2008 Wii releases bytes +8..+11 are `5b 80 80 8d` in 2,051 payloads of
     2,051, which is what a compressor's fixed preamble looks like;
  4. **the cast and the project tags**, asked of the *names*, where a hit is not
     a chance survivor the way it is in a raw byte sweep.

    python crosstitle.py IMAGE MODULEDIR --other DIR [--other DIR ...]
    python crosstitle.py IMAGE MODULEDIR --other-rom IMAGE2 MODULEDIR2

`--other-rom` runs the identical container descent over the second cartridge,
so the two sides are payload lists rather than file lists and the comparison is
between like and like.  `--other DIR` compares against a plainly extracted tree,
which is what the other pipelines in the corpus publish.

Standard library only.
"""

import collections
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census
import fps4

CAST = ["rutee", "stahn", "dimlos", "cress", "reid", "veigue", "senel", "luke",
        "emil", "marta", "richter", "lloyd", "colette", "genis", "zelos",
        "yuri", "estelle", "karol", "repede", "judith", "flynn", "rita",
        # and this cartridge's own, which is the control on the search itself:
        "shing", "kohaku", "hisui", "beryl", "innes", "kunzite", "chalcedony",
        "lithia", "incarose"]
TAGS = ["top2", "to7", "to8", "to9", "tods", "tor", "tol", "tos", "t8bt",
        "nt_ds1", "ezbind", "mscf", "fps4", "v154"]


def this_payloads(image, moddir):
    """Yield (name, bytes) for every payload the census enumerates.

    Using the census's own enumerator rather than a second walk is deliberate:
    two tools that descend a nested container in two different ways report two
    different denominators for one cartridge, and then the reader has to guess
    which is the cartridge.
    """
    en = census.Enumerator(image, moddir)
    for label, buf in en.payloads():
        if buf:
            yield (label, bytes(buf))


def tree_files(root):
    for r, _ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            try:
                with open(p, "rb") as fh:
                    yield (p, fh.read())
            except OSError:
                continue


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    image = argv[1]
    moddir = argv[2]
    others = [argv[i + 1] for i, a in enumerate(argv) if a == "--other"]
    other_roms = [(argv[i + 1], argv[i + 2])
                  for i, a in enumerate(argv) if a == "--other-rom"]

    # One pass over six gigabytes, not three: the SHA-1 index, the name list
    # and both preamble tables are all built from the same walk.
    mine = collections.defaultdict(list)
    my_names = collections.Counter()
    n_mine = b_mine = 0
    xc_cols = [collections.Counter() for _ in range(16)]
    bl_cols = [collections.Counter() for _ in range(16)]
    n_xc = n_bl = 0
    for name, buf in this_payloads(image, moddir):
        mine[hashlib.sha1(buf).digest()].append(name)
        my_names[os.path.basename(name).lower()] += 1
        n_mine += 1
        b_mine += len(buf)
        if len(buf) >= 16 and buf[:4] == bytes.fromhex("0ff512ee"):
            for k, b in enumerate(buf[:16]):
                xc_cols[k][b] += 1
            n_xc += 1
        elif len(buf) >= 26 and buf[0] in (0, 1, 3):
            packed, unpacked = struct.unpack_from("<II", buf, 1)
            if packed + 9 == len(buf) and 0 < unpacked <= 0x8000000:
                for k, b in enumerate(buf[9:25]):
                    bl_cols[k][b] += 1
                n_bl += 1

    print("=== 1. whole payloads, by SHA-1")
    print("this disc      %s payloads, %s distinct, %s bytes"
          % (format(n_mine, ","), format(len(mine), ","), format(b_mine, ",")))

    for oimage, omod in other_roms:
        theirs = collections.defaultdict(list)
        their_names = collections.Counter()
        n = 0
        b = 0
        for p, buf in this_payloads(oimage, omod):
            theirs[hashlib.sha1(buf).digest()].append(p)
            their_names[os.path.basename(p).lower()] += 1
            n += 1
            b += len(buf)
        common = set(mine) & set(theirs)
        print("%-14s %s payloads, %s distinct, %s bytes -- byte-identical: %s"
              % (os.path.basename(oimage), format(n, ","),
                 format(len(theirs), ","), format(b, ","),
                 format(len(common), ",")))
        shared = sorted(set(my_names) & set(their_names))
        print("      shared names, basename and case-folded: %s of %s against %s"
              % (format(len(shared), ","), format(len(my_names), ","),
                 format(len(their_names), ",")))
        differ = sorted(set(my_names) ^ set(their_names))
        print("      names on one side only: %s" % format(len(differ), ","))
        for nm in differ[:40]:
            print("         %s" % nm)
        onlymine = [nm for h, nm in mine.items() if h not in theirs]
        print("      payloads on this side only: %s of %s"
              % (format(len(onlymine), ","), format(len(mine), ",")))
        for nm in sorted(x[0] for x in onlymine)[:40]:
            print("         %s" % nm)

    for root in others:
        theirs = collections.defaultdict(list)
        their_names = collections.Counter()
        n = 0
        for p, buf in tree_files(root):
            theirs[hashlib.sha1(buf).digest()].append(p)
            their_names[os.path.basename(p).lower()] += 1
            n += 1
        common = set(mine) & set(theirs)
        print("%-14s %s files, %s distinct -- byte-identical: %s"
              % (os.path.basename(root), format(n, ","),
                 format(len(theirs), ","), format(len(common), ",")))
        for h in list(common)[:20]:
            print("      %s   <->   %s" % (mine[h][0], theirs[h][0]))
        shared = sorted(set(my_names) & set(their_names))
        print("      shared names, basename and case-folded: %s of %s against %s"
              % (format(len(shared), ","), format(len(my_names), ","),
                 format(len(their_names), ",")))
        for nm in shared[:40]:
            print("         %s" % nm)

    print()
    print("=== 2. the compressor's preamble, position by position")
    print("A column with one distinct value is a constant the compressor")
    print("writes; a column with 256 is random.  For the block codec the")
    print("window starts at +9, which is the first byte of the stream and")
    print("therefore the first control byte, not the header.")
    for kind, cols, n in (("XCompress streams, from +0", xc_cols, n_xc),
                          ("codec block streams, from +9", bl_cols, n_bl)):
        print()
        print("  %s: %s payloads" % (kind, format(n, ",")))
        print("  %-6s %8s  %s" % ("OFFSET", "DISTINCT", "MOST COMMON VALUE"))
        for k, c in enumerate(cols):
            if not c:
                continue
            v, cnt = c.most_common(1)[0]
            print("  +%-5d %8d  0x%02X in %s of %s"
                  % (k, len(c), v, format(cnt, ","), format(n, ",")))
    print()
    print("  the 2003 GameCube and 2008 Wii figure, for comparison:")
    print("  +8..+11 are 5b 80 80 8d in 2,051 of 2,051 MSCF payloads, with")
    print("  the four bytes in front of them uniformly random.")

    print()
    print("=== 3. the cast and the project tags, in this disc's own names")
    print("%-10s %6s  %s" % ("NEEDLE", "NAMES", "THE NAMES THEMSELVES"))
    for w in CAST + [None] + TAGS:
        if w is None:
            print()
            continue
        hits = sorted(nm for nm in my_names if w in nm)
        print("%-10s %6s  %s"
              % (w, format(len(hits), ","), ", ".join(hits[:8])))
    print()
    print("   denominator: %s distinct member names" % format(len(my_names), ","))
    print("   Ratatosk's own figure: 0 of 734 MSCF member names shared with")
    print("   2003, and 0 of 71,353 internal names from any other title.")


if __name__ == "__main__":
    main(sys.argv)
