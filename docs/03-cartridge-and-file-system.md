# The cartridge and its file system

Everything on this page is read from the two images' own structures with
[`tools/ndsrom.py`](../tools/ndsrom.py). Nothing is taken from a file name.

## The header

| Field | Anime | CG |
|---|---|---|
| internal title | `TOHHEARTSANM` | `TOHHEARTSCG` |
| game code | `CTUJ` | `CTGJ` |
| maker code | `AF` | `AF` |
| unit code | `0x00` (NTR, DS-only) | `0x00` |
| encryption seed | `0x00` | `0x00` |
| device capacity | `0x0B` → 268,435,456 bytes | `0x0B` |
| region | `0x00` (Japan / free) | `0x00` |
| ROM version | `0x00` | `0x00` |
| header CRC | `0xA445`, recomputes | `0xC860`, recomputes |
| logo CRC | `0xCF56` — the retail value | `0xCF56` |
| secure area CRC | `0x5666` | `0x1EBB` |
| debug fields `+0x160..0x17F` | all zero | all zero |
| declared used size | 249,787,044 | 245,000,868 |
| actual highest file end | 249,787,044 | 245,000,868 |

The declared size and the highest file end agree exactly on both, so nothing on
either cartridge sits outside what the header claims.

## The layout

| Region | Offset | Bytes |
|---|---:|---:|
| header and its slack | 0x0 | 16,384 |
| ARM9, `BLZ`-packed | 0x4000 | 432,924 / 432,920 |
| overlay table (31 entries) | 0x6DC00 | 992 |
| the 31 overlays, all `BLZ`-packed | 0x6DFE0… | 1,028,328 |
| ARM7, not packed | 0x16AE00 | 159,528 |
| file name table | 0x191E00 | 42,281 |
| file allocation table | 0x19C400 | 41,160 |
| banner | 0x1A6600 | 2,560 |
| the 5,114 named files | 0x1A9000… | |
| tail, all `0xFF` | 0xEE372A4 / 0xE9A6AA4 | 18,648,412 / 23,434,588 |

## The file system

5,145 FAT entries: 5,114 named files and 31 unnamed, which are the overlays.
23 directories.

| Directory | Files | Bytes |
|---|---:|---:|
| `/s` | 4,458 | 112,185,686 |
| `/s/lvd` | 518 | 11,888 |
| `/menu` | 22 | 1,725,464 |
| `/m` | 9 | 79,692,567 |
| `/m/misc/2D` | 18 | 390,168 |
| `/m/misc/etc` | 12 | 285,940 |
| `/movie` | 10 | 25,775,082 |
| `/title` | 10 | 319,519 |
| `/item` | 10 | 87,645 |
| `/btl/char` | 2 | 15,286,004 |
| `/btl/map` | 2 | 4,790,796 |
| `/btl/magic` | 2 | 2,238,948 |
| `/fc` | 4 | 1,976,032 |
| `/btl/debug` | 2 | 91,628 |
| the root | 13 | 307,787 |
| (nine more) | | |

[`reports/anime-files.txt`](../reports/anime-files.txt).

Two things in that table are worth a sentence each. `/s` holds 4,456 voice
files with no extension and one 21 MB sound archive; the 518 files in `/s/lvd`
are one small file per voice line. And **`/btl/debug` shipped**, 91,628 bytes
of it — [10](10-leftovers.md).

## Classification is by magic, never by extension

63 files are named `.dat` and they are at least five different things. Reading
the first four bytes of every file instead:

| First bytes | Files | Bytes | What |
|---|---:|---:|---|
| `80 00` | 4,456 | 91,033,886 | CRI ADX-family header — all of them AHX |
| `FPS4` | 56 | 75,058,264 | the studio's archive |
| `V154` | 19 | 24,577,038 | the studio's second container |
| `MODS` | 9 | 25,775,032 | Actimagine Mobiclip |
| `SDAT` | 1 | 21,146,560 | NitroSDK sound archive |
| `0F 00` | 518 | 11,888 | `/s/lvd`, one per voice line |
| `RTFN` | 3 | 141,916 | NitroSDK fonts (`NFTR`) |
| `10 xx` / `11 xx` | 15 | 5,872,380 | BIOS `LZ77` / `LZ11` streams |
| other | 105 | | tables and unclassified |

Two of those rows are traps the corpus has already recorded once. The 4,456
files beginning `80 00` would be counted as BIOS difference-filter streams by a
census that had the filter type bytes one place low — the defect *Tales of
Innocence* found, where 2,444 CRI files were reported as `Diff8`. And the
`FPS4`/`V154` rows are containers, so a census that stops at the file level
reports 75 payloads where there are 47,195. [08](08-containers-and-assets.md).

## The unused space, and what it is made of

| | Anime | CG |
|---|---:|---:|
| alignment slack between files | 1,449,281 (0.54%) | 1,449,257 (0.54%) |
| tail after the last file | 18,648,412 (6.95%) | 23,434,588 (8.73%) |
| **total unused** | **7.49%** | **9.27%** |

The slack samples ten distinct byte values in its first mebibyte, 1,449,269 of
which are `0xFF`. The tail samples **one**: `0xFF`, in all 4,194,304 bytes
sampled, and it deflates to **0.0974%** of itself.

That last number is the point. On *Tales of Vesperia* a 19.08% region that
looked empty turned out to be incompressible pseudo-random fill and was not
free space at all, so the rule since then is to profile anything that looks
like filler before writing it down. Here it profiles as genuinely free: a
single byte value, compressible to a thousandth of itself.

For comparison across the corpus's cartridges: *Tales of the Tempest* left
**41.3%** unused, *Tales of Innocence* **3.2%**. These two are between them,
and the difference between them is entirely the film.

[`reports/anime-budget.txt`](../reports/anime-budget.txt),
[`reports/cg-budget.txt`](../reports/cg-budget.txt).
