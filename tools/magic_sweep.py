#!/usr/bin/env python3
"""Sweep the whole partition for every container tag the corpus knows.

Three families of needle:

  * **the corpus's own** -- the envelopes and project tags of the twelve
    *Tales* builds documented so far, plus the middleware stamps that turned up
    beside them, plus the two names -- `stan` and `dimlos` -- that *Tales of
    the Tempest* raised and *Tales of Innocence* did not settle;
  * **the direct prequel's** -- what the 2003 GameCube release of this game
    carries, read out of that repository rather than invented: `MSCF`, `top2`,
    `Top2Btl`, `_custom`, `rutee`, `tod2_cut`, `h4m`, `HVQM4`;
  * **the middleware** anyone might have bought instead.

**Read the chance rate before reading any count.**  A four-byte needle turns
up by chance about once per 4 GB of uniform data.  The reading of a count
therefore changes with the size of the medium and the count alone does not say
so:

    Tales of Innocence, 128 MB cartridge      0.031 expected hits
    Tales of Hearts, 256 MiB cartridge        0.063 expected hits
    Ratatosk no Kishi, 4.29 GB Wii partition  1.00  expected hits
    Tales of Vesperia, 7.84 GB XGD2 image     1.82  expected hits

On the two discs a single hit means nothing and a zero is weak.  On a
cartridge the rate is small enough that **a single hit is worth locating and a
zero is strong** -- the denominator points the ordinary way round, which after
two disc-sized targets is worth saying out loud.  The table prints the
expected rate beside every needle so the two kinds are never mixed.

Longer needles are worth much more here, and the table prints the expected
rate for each so the two kinds are never mixed.

    python magic_sweep.py PARTITION.bin
    python magic_sweep.py PARTITION.bin --context

Standard library only.
"""

import os
import sys

CORPUS = [
    (b'CPS ', 'Legendia 2005, the sixteen-byte envelope'),
    (b'CPS\x00', 'Legendia 2005, other spelling'),
    (b'TLPS', 'Tales container tag'),
    (b'TLPK', 'Tales container tag'),
    (b'AFS\x00', 'CRI AFS archive'),
    (b'SCPK', 'Destiny 2 2002 bundle'),
    (b'THEIRSCE', 'Tales script container'),
    (b'FILE.FPB', 'Destiny 2 2002 archive name'),
    (b'FPS2', 'Rebirth / Abyss archive'),
    (b'FPS3', 'Rebirth / Abyss archive'),
    (b'FPS4', 'Tales archive, later builds'),
    (b'MSCF', "the studio's own envelope, 2003 and here"),
    (b'CVMH', 'CRI CVM volume header'),
    (b'ROFSBLD', 'CRI ROFS builder stamp'),
    (b'SAMPLE_GAME_TITLE', 'CRI builder default title'),
    (b'TO7', 'Abyss project tag'),
    (b'TO8', 'project tag, next in the series'),
    (b'ToR', 'Rebirth project tag'),
    (b'ToL', 'Legendia project tag'),
    (b'tox', 'Legendia project directory'),
    (b'tor_', 'Rebirth effect prefix, found on the Abyss disc'),
    (b'no_se_', 'Rebirth sound-effect prefix'),
    (b'stan', 'Tempest 2006 name, raised and unresolved'),
    (b'dimlos', 'Tempest 2006 name, raised and unresolved'),
    (b'EZBIND', 'Innocence 2007 archive'),
    (b'NT_DS1', 'Tempest 2006 project tag'),
    (b'To9', 'the next project number after Vesperia'),
    (b'TO9', 'the same, upper case'),
    (b'TODS', 'the DS project tag on the 2008 cartridges'),
    (b'TODS3', 'the same, with its number'),
    (b'CTODS3', 'the same, item-table spelling'),
    (b'V154', 'the second container on the 2008 cartridges'),
    (b'MODS', 'Actimagine Mobiclip video'),
    (b'VXDS', 'Actimagine VX video, the 2006 cartridge'),
    (b'MOC5', 'Actimagine Mobiclip, other spelling'),
    (b'SDAT', 'the NitroSDK sound archive'),
    (b'BLZ\x00', 'the Nintendo linker backwards LZ, as a string'),
    (b'(c)CRI', 'CRI copyright, stamped in ADX and AHX headers'),
    (b'CRI ', 'CRI middleware'),
    (b'shing', 'Hearts 2008, the male lead'),
    (b'kohaku', 'Hearts 2008, the female lead'),
    (b'beryl', 'Hearts 2008, party'),
    (b'hisui', 'Hearts 2008, party'),
    (b'innes', 'Hearts 2008, party'),
    (b'kunzite', 'Hearts 2008, party'),
    (b'yuri', 'Vesperia 2008, the male lead'),
    (b'estelle', 'Vesperia 2008'),
    (b'karol', 'Vesperia 2008'),
    (b'rita', 'Vesperia 2008'),
    (b'raven', 'Vesperia 2008'),
    (b'judith', 'Vesperia 2008'),
    (b'flynn', 'Vesperia 2008'),
    (b'repede', 'Vesperia 2008'),
    (b'YUR', 'Vesperia 2008, the three-letter form its assets use'),
    (b'EST', 'Vesperia 2008, three-letter form'),
    (b'KAR', 'Vesperia 2008, three-letter form'),
    (b'luke', 'Abyss 2005'),
    (b'emil', 'Ratatosk 2008'),
    (b'marta', 'Ratatosk 2008'),
    (b'lloyd', 'Symphonia 2003'),
    (b'veigue', 'Rebirth 2004'),
    (b'senel', 'Legendia 2005'),
    (b'reid', 'Eternia 2000'),
    (b'cress', 'Phantasia 1995'),
]

PREQUEL = [
    (b'top2', 'the 2003 project name, from `top2.c`'),
    (b'Top2', 'the 2003 relocatable modules'),
    (b'_custom', 'the one team-named map that shipped in 2003'),
    (b'rutee', 'the 2003 disc, a character from Tales of Destiny'),
    (b'tod2_cut', 'the 2003 movie table, named after Destiny 2'),
    (b'HVQM4', "Hudson's video codec, the 2003 disc's"),
    (b'.h4m', 'the 2003 movie extension'),
    (b'testfield', 'the 2003 test maps'),
    (b'BTLenemy', 'the 2003 file that held 251 codec blocks'),
    (b'ToSM', "this build's own sound-archive tag"),
    (b'TOSM', "this build's own sound-archive tag, upper case"),
    (b'RT4J', 'this game id'),
]

MIDDLEWARE = [
    (b'CRID', 'CRI Sofdec 2'),
    (b'@UTF', 'CRI table format'),
    (b'ADXF', 'CRI ADX'),
    (b'AHXF', 'CRI AHX'),
    (b'Sofdec', 'CRI video'),
    (b'CRI ', 'CRI Middleware'),
    (b'criware', 'CRI Middleware'),
    (b'VXDS', 'Actimagine VX'),
    (b'MODS', 'Actimagine Mobiclip'),
    (b'Bink', 'RAD Game Tools Bink'),
    (b'Miles', 'RAD Game Tools Miles'),
    (b'Havok', 'Havok physics'),
    (b'Granny', 'RAD Granny'),
    (b'FMOD', 'Firelight FMOD'),
    (b'zlib', 'zlib'),
    (b'inflate', 'zlib'),
    (b'PK\x03\x04', 'zip local header'),
    (b'\x1f\x8b\x08', 'gzip'),
]

# Added for the fourteenth build.  Everything the *platform* supplies, so that
# "what does it use instead" is asked with the same instrument as "does it use
# the format" -- and the cast of every title in the corpus, so the cross-title
# question is asked in both directions at once.
XBOX360 = [
    (bytes.fromhex('0ff512ee'), 'XCompress stream magic (XDK LZX)'),
    (b'XCompress', 'the XDK compression library, by name'),
    (b'XMemCompress', 'the XDK compression entry point'),
    (bytes.fromhex('3026b275'), 'ASF / Windows Media header GUID'),
    (b'WAVEXMA2', 'XMA2 audio in a RIFF WAVE'),
    (b'XUIZ', 'XUI, the XDK user-interface package'),
    (b'XDBF', 'the title metadata database'),
    (b'XEX2', 'an Xbox 360 executable'),
    (b'SLZ', 'the tri-Ace wrapper around XCompress'),
    (b'Aska', "tri-Ace's engine namespace"),
    (b'ASKA', "tri-Ace's engine namespace, upper case"),
    (b'.cpp', 'a source path left in the image'),
    (b'\\Release', 'a Windows build path'),
    (b'../Release/', 'a POSIX-style build path'),
]

CAST = [
    (b'rutee', 'Destiny 1997 / Symphonia 2003'),
    (b'stahn', 'Destiny 1997'),
    (b'dimlos', 'Destiny 1997'),
    (b'cress', 'Phantasia 1995'),
    (b'reid', 'Eternia 2000'),
    (b'veigue', 'Rebirth 2004'),
    (b'senel', 'Legendia 2005'),
    (b'luke', 'Abyss 2005'),
    (b'emil', 'Ratatosk 2008, six weeks earlier'),
    (b'marta', 'Ratatosk 2008, six weeks earlier'),
    (b'richter', 'Ratatosk 2008, six weeks earlier'),
    (b'lloyd', 'Symphonia 2003 and Ratatosk 2008'),
    (b'yuri', 'this game'),
    (b'estelle', 'this game'),
    (b'karol', 'this game'),
    (b'repede', 'this game'),
    (b'judith', 'this game'),
    (b'flynn', 'this game'),
]


def sweep(path, needles, chunk=1 << 24):
    counts = dict((n, 0) for n, _ in needles)
    first = dict((n, []) for n, _ in needles)
    maxn = max(len(n) for n, _ in needles)
    # The tables overlap on purpose -- `rutee` and `dimlos` are each named in
    # two of them, because each table is meant to be readable on its own.  The
    # *scan* must still see every needle once: searching the same bytes twice
    # counts every hit twice and turns one chance survivor into two, which is
    # exactly the kind of number this tool exists to keep honest.
    needles = list(dict.fromkeys(n for n, _ in needles).keys())
    needles = [(n, "") for n in needles]
    f = open(path, 'rb')
    pos = 0
    prev = b''
    while True:
        buf = f.read(chunk)
        if not buf:
            break
        blob = prev + buf
        base = pos - len(prev)
        for n, _why in needles:
            i = 0
            while True:
                i = blob.find(n, i)
                if i < 0:
                    break
                # The carried-over tail exists so a needle can straddle the
                # seam.  A match that lies *entirely* inside it was already
                # found and counted in the previous chunk, so counting it again
                # inflates every short needle by however many seams it happens
                # to sit near -- which is how `rutee` came back as two hits at
                # one offset.  Require the match to reach into the new data.
                if i + len(n) <= len(prev):
                    i += 1
                    continue
                counts[n] += 1
                if len(first[n]) < 6:
                    first[n].append(base + i)
                i += 1
        prev = blob[-(maxn - 1):] if maxn > 1 else b''
        pos += len(buf)
    return counts, first, pos


def table(title, needles, counts, first, size, context, path):
    print()
    print('=== %s' % title)
    print('%-20s %8s %10s  %s'
          % ('NEEDLE', 'HITS', 'EXPECTED', 'WHAT IT WOULD MEAN'))
    for n, why in needles:
        exp = size / float(256 ** min(len(n), 8))
        print('%-20s %8s %10s  %s'
              % (repr(n)[1:][:20], '{:,}'.format(counts[n]),
                 ('%.3g' % exp) if exp >= 0.001 else '<0.001', why))
        if context and counts[n] and first[n]:
            f = open(path, 'rb')
            for o in first[n]:
                f.seek(max(0, o - 16))
                b = f.read(48)
                print('        0x%010X  %s' % (o, b.hex()))


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    path = argv[1]
    context = '--context' in argv
    all_needles = CORPUS + PREQUEL + MIDDLEWARE + XBOX360 + CAST
    counts, first, size = sweep(path, all_needles)
    print('image %s, %s bytes' % (os.path.basename(path), '{:,}'.format(size)))
    print('a four-byte needle has a chance rate of %.2f on this medium;'
          % (size / 4294967296.0))
    print('a single hit is therefore not evidence and a zero is weak.')
    print('This is the largest medium the corpus has opened, so the inversion')
    print('section 7 describes is more marked here than anywhere before it.')
    table('the corpus', CORPUS, counts, first, size, context, path)
    table('the 2003 GameCube prequel', PREQUEL, counts, first, size,
          context, path)
    table('middleware', MIDDLEWARE, counts, first, size, context, path)
    table('what this platform supplies', XBOX360, counts, first, size,
          context, path)
    table('the cast of every title in the corpus', CAST, counts, first, size,
          context, path)


if __name__ == '__main__':
    main(sys.argv)
