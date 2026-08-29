# What it compresses with instead

Section 7's rule for a new target is to ask what the platform hands you for
free before proving a custom codec absent. The Nintendo DS hands you six
decompression services through a `SWI`, and its linker hands you a seventh,
`BLZ`, for the executable.

This cartridge uses the formats heavily and **calls none of the services**. The
two halves are reported separately because they are two different findings and
they are allowed to disagree.

## Half one: the data is in the platform's formats

| | Anime | CG |
|---|---:|---:|
| whole **files** that are a BIOS stream | 11 of 5,145 | 11 of 5,145 |
| those files, packed → plain | 68,140 → 113,564 | same |
| **BIOS streams inside the containers** | **5,280** | **5,280** |
| those, packed → plain | **61,737,814 → 123,245,746** (2.00×) | same |
| of which `LZ77` | 4,034 | 4,034 |
| of which `LZ11` | 1,246 | 1,246 |

[`reports/anime-census.txt`](../reports/anime-census.txt),
[`reports/anime-bios-formats.txt`](../reports/anime-bios-formats.txt).

**The file-level number is the one that would have been wrong.** Eleven of
5,145 files reads like a build that barely compresses; 5,280 streams turning
61.7 MB into 123.2 MB reads like a build whose entire asset pipeline is
compressed. Both are true, and only the second describes the cartridge, because
this build compresses **inside its containers** rather than at the file level.
A census that stops at the Nitro file system reports the first.

For comparison, *Tales of Innocence* — which does compress at the file level —
has 102 `LZ77` files turning 16,901,069 into 32,116,356, and *Tales of the
Tempest* has zero of 4,712.

### What is falsifiable and what is not

Only `LZ77` can be ruled out by decoding: it rejects a back-reference before
the start of the output and its geometry caps the ratio at 18 / 2.125 = 8.47×.
`RLE`, the two difference filters and a small Huffman tree accept almost
anything, and `LZ11`'s four-byte token reaches 65,808 output bytes so no ratio
bound constrains it. The 1,246 `LZ11` streams are counted because the decode
consumed the whole payload exactly, which is a weaker test, and the census
prints that sentence beside the number.

### And the cartridge names its own compression

Six files carry it in the name — `Menu_Event.NCGR_lz`, `TITLE_LOGO_NAMCO.NSCR_lz`,
`game_over.NCLR_lz` and their siblings — and all six are `LZ11`. Two more,
`/btl/common/face_LZ.bin` and `/m/hsr.bin`, are `LZ77`. Inside the containers
the same convention runs on: `03d_LZ.bin`, `d_LZ.bin`, `02d_stk_LZ.bin`,
`03d_win_LZ.bin`.

## Half two: the build calls none of the services

The SDK links a table of `svc #N ; bx lr` wrappers into the ARM9 whether or not
anything uses them, so their presence says only that the library was linked.
The measurement is the caller count.

Every branch in all 33 modules was resolved, **including across the module
boundary** — the wrappers are linked once, into the ARM9's secure area, so an
overlay that wanted one would branch out of its own image and leave no call
site a single-image count could see ([`tools/bios_calls.py --also`](../tools/bios_calls.py)):

| | Anime | CG |
|---|---:|---:|
| distinct branch targets resolved, all 33 images | **43,946** | **43,954** |
| decompression wrappers linked | 6 | 6 |
| **callers of any of them** | **0** | **0** |
| callers of `CpuSet` | 1 | 1 |
| callers of `Stop/Sleep` | 7 | 7 |

The six linked decompression services are `BitUnPack` (`0x10`),
`LZ77UnCompReadNormalWrite8bit` (`0x11`), `LZ77UnCompReadByCallbackWrite16bit`
(`0x12`), `HuffUnCompReadByCallback` (`0x13`), `RLUnCompReadNormalWrite8bit`
(`0x14`) and `RLUnCompReadByCallbackWrite16bit` (`0x15`). Not one has a call
site.

The last two rows are the control: the instrument finds callers where there are
callers. And those eight call sites have a second life — they are **exactly**
the eight addresses at which the two editions' `arm9.bin` differ
([02](02-the-two-editions.md)), found by a different tool asking a different
question.

[`reports/anime-bios-calls.txt`](../reports/anime-bios-calls.txt),
[`reports/cg-bios-calls.txt`](../reports/cg-bios-calls.txt).

## So something decompresses these in software, and the probe did not find it

This is the same conclusion *Tales of Innocence* reached and the same
instrument reached it. `lzprobe.py` looks for the format's arithmetic rather
than for the service — the length nibble, the `+3`, the low nibble, the
twelve-bit join, and the halfword-token and `do/while` variants — and counts
co-locations with their denominators.

Over the ARM9 it returns 66 THUMB `lsr #12` sites within 40 instructions of a
`+3`, and zero for the ARM forms of the nibble-split pattern; over the
overlays, 16 and fewer. **A co-location on its own is noise at those
denominators**, and no site carries enough of the fingerprints together to name
a routine. The probe is published with that stated and with its counts, as it
was on *Tales of Innocence*, where it also failed.
[`reports/anime-lzprobe.txt`](../reports/anime-lzprobe.txt).

Two things are known about the routine even so: it is not the BIOS, because
nothing branches to a wrapper and no wrapper address occurs as a data word; and
it handles **both** `LZ77` and `LZ11`, because both appear inside the
containers in quantity.

## `BLZ`, the seventh

The linker's own backwards LZ is the one compressor this build demonstrably
uses through the platform's tooling, and it is applied to 32 of the 33 modules.
The `BLZ` decoder is not a `SWI`; the NitroSDK links a copy into the ARM9's
autoload path, which is why it needs no call site.

| | |
|---|---:|
| modules packed | 32 of 33 |
| on the cartridge | 1,620,780 bytes |
| in plaintext | 2,852,064 bytes |
| **the linker's compression ratio** | **56.8%** |

And measured the other way, by deflate
([`tools/deflate_control.py`](../tools/deflate_control.py)): the packed modules
deflate to **88.88%** of themselves and the plaintext to **46.93%**, which is
what an already-compressed stream and an uncompressed one look like side by
side.

## The counter-check that depends on no probe at all

Run the whole thing through `zlib` and report **by class**, because the total
averages together things that are not comparable
([`reports/anime-deflate.txt`](../reports/anime-deflate.txt)):

| Class | Count | Bytes | Deflates to |
|---|---:|---:|---:|
| container (`FPS4` / `V154`) | 75 | 99,635,302 | **75.65%** |
| voice (CRI AHX) | 4,456 | 91,033,886 | 93.26% |
| video (Mobiclip) | 10 | 25,775,082 | 99.03% |
| sound archive (`SDAT`) | 1 | 21,146,560 | 81.61% |
| BIOS-format streams, whole files | 15 | 5,872,380 | 89.48% |
| **everything else** | 557 | 3,150,396 | **31.41%** |
| executable, `BLZ`-packed as shipped | 32 | 1,461,252 | 88.88% |
| executable, `BLZ` plaintext | 33 | 2,852,064 | **46.93%** |
| executable, ARM7 (not packed) | 1 | 159,528 | 54.01% |
| the unused tail | 1 | 18,648,412 | **0.10%** |
| **the whole image as one buffer** | | 268,435,456 | **78.24%** |

Set beside the corpus:

| Build | Whole medium | Compressed class / raw class |
|---|---:|---|
| *Tales of the Tempest*, DS 2006 | 52.6% | data stored raw |
| *Tales of Innocence*, DS 2007 | 73.5% | 91.27% / 52.23% |
| *Ratatosk no Kishi*, Wii 2008 | — | 89.62% / 50.74% |
| *Tales of Vesperia*, Xbox 360 2008 | — | 99.20% / 33.19% |
| **this cartridge** | **78.24%** | **75.65% / 31.41%** |

The split is the reading, not the total. The 31.41% row is everything that is
not a container, a media file or an executable — 3.1 MB of tables and
uncompressed data, which deflates like plain data because it is. The 75.65% row
sits below *Innocence*'s 91.27% because the containers are a mixture: 5,280
BIOS-compressed members inside them, and the rest stored. This build compresses
most of what it puts in a container and not all of it, and 75.65% is what that
mixture looks like from outside.

The last row of the first table is the one that settles a question
[03](03-cartridge-and-file-system.md) raises: 18.6 MB of tail deflating to
0.10% is free space, not the incompressible pseudo-random fill that fooled the
*Vesperia* budget.
