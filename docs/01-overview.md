# Overview

*Tales of Hearts*, Nintendo DS, Namco Bandai Games, 18 December 2008, Japan
only. Two cartridges shipped on that day and this repository documents both.

Everything below is read out of the two images. Nothing is taken from a
catalogue, a file name or a release database, and where a claim rests on
something outside the bytes it is labelled **Consistent** or **Open** rather
than **Verified**.

## What the two cartridges say they are

| | Anime Movie Edition | CG Movie Edition |
|---|---|---|
| internal title | `TOHHEARTSANM` | `TOHHEARTSCG` |
| game code | `CTUJ` | `CTGJ` |
| maker code | `AF` | `AF` |
| device capacity byte | `0x0B` = 268,435,456 | `0x0B` = 268,435,456 |
| image size | 268,435,456 | 268,435,456 |
| declared used | 249,787,044 | 245,000,868 |
| header CRC | `0xA445`, recomputes | `0xC860`, recomputes |
| Nintendo logo CRC | `0xCF56`, the retail value | `0xCF56`, the retail value |
| FAT entries | 5,145 | 5,145 |
| named files | 5,114 | 5,114 |
| directories | 23 | 23 |
| ARM9 overlays | 31 | 31 |
| ARM7 overlays | 0 | 0 |

The banner is UTF-16 and carries the same six language slots on both, all six
holding the Japanese string:

```
テイルズ オブ ハーツ
アニメムービーエディション        CG のほうは CGムービーエディション
バンダイナムコゲームス
```

[`reports/anime-modules.txt`](../reports/anime-modules.txt),
[`reports/cg-modules.txt`](../reports/cg-modules.txt).

## The headline

**The block codec is not here.** Across thirty-three executable modules on each
cartridge — an ARM9, an ARM7 and thirty-one overlays, **thirty-two of which are
`BLZ`-packed and had to be decompressed first** — the scan finds not one
`4078`, `4079`, `4070` or `4071` in either of the two encodings ARM has for
them, out of

| | |
|---|---:|
| ARM data-processing immediates | **201,427** |
| THUMB instructions carrying a literal | **106,319** |
| 4-byte-aligned words | **713,016** |
| distinct PC-relative load targets | **27,133** |

and the unmodified reference decoder, run blind at every offset of every
payload in both dialects, returns **0 blocks in 47,195 payloads and
376,083,362 bytes** while returning the 1995 cartridge's **1,089** in the same
invocation. [06](06-the-codec.md).

**And this is the control the corpus has been asking for since 2006.** The two
Nintendo DS cartridges already in the corpus are *Tales of the Tempest* (Dimps,
2006) and *Tales of Innocence* (Alfa System, 2007), both from studios outside
the line that carried the codec from 1995 to 2005, and both open questions say
in nearly the same words that what is needed is a DS title *from* that line.
This cartridge carries the project tag **`TO9`** — the next number after `TO7`
(*Tales of the Abyss*, 2005) and `TO8` (*Tales of Vesperia*, 2008), both
confirmed line builds — in its file names, in a file extension of its own
(`.to9moh`, 107 names) and in a debug overlay's version banner beside its build
date. [11](11-cross-title.md).

**But the cartridge does not name its developer**, in any of the three
alphabets, and that condition is carried through everything written here.
[05](05-who-made-it.md).

## What is here instead

| | |
|---|---|
| container | **`FPS4`**, little-endian — the same container as *Tales of Vesperia* five months earlier, where it is big-endian, with the same field-mask semantics |
| second container | **`V154`**, 1,508 objects, stating its own length in two halves |
| compression | the platform's own — **5,280 BIOS streams** inside the containers, and `BLZ` on 32 of 33 modules |
| but not the platform's *service* | **zero callers** of all six linked decompression wrappers over **43,946** resolved branch targets, across the module boundary |
| video | Actimagine **Mobiclip** `MODS`, 256×192, 23.976 fps |
| voice | CRI **AHX**, 4,456 files, 5 h 56 m — with **no `[SDK+CRI:…]` tag anywhere** |
| music | NitroSDK `SDAT`, 532 members, 36 m 32 s of streamed music |

## The two editions are one build

This is the control the corpus has never had on a cartridge, and it is free.
Running the identical container descent over both images and comparing payload
by payload:

**28,662 of 28,679 distinct payloads are byte-identical.** Seventeen differ,
and every one of the seventeen is the edition or a structure that moves because
of it: the nine movies, `/movie/memo.txt`, the ROM header, the banner, the
file allocation table, two alignment regions, the tail, and `arm9.bin` — whose
plaintext differs in 2,045 bytes of regenerated secure-area filler, eight
`BLX` offsets into it, and one byte of its own packed length.

Every measurement in this repository therefore transfers between the two
cartridges by identity rather than by repetition, and both were run anyway.
[02](02-the-two-editions.md).

## Status of every claim

| Claim | Status |
|---|---|
| The block codec is absent from both cartridges | **Verified** — 201,427 + 106,319 + 713,016 denominators, 0 blocks in 376,083,362 bytes, control returns 1,089 |
| Thirty-two of thirty-three modules are `BLZ`-packed | **Verified** — three independent statements agree, and 31 of 31 overlays decompress to their declared length |
| The container is `FPS4`, little-endian | **Verified** — 2,492 archives read, 2,493 magic hits |
| The build calls no BIOS decompression service | **Verified** — 0 of 6 wrappers over 43,946 targets |
| The data is nonetheless in BIOS formats | **Verified** — 5,280 streams that decode and consume themselves exactly |
| The two editions are one build with one asset group swapped | **Verified** — 28,662 of 28,679 payloads identical, all 17 differences located |
| The cartridge does not name its developer | **Verified** — zero in ASCII, Shift-JIS and UTF-16LE |
| The build was compiled with RTTI off | **Verified** — 5 C++ names in 2,852,064 bytes, all standard library |
| `TO9` is this project's tag in the same scheme as `TO7` and `TO8` | **Consistent** — the string is in the bytes; the scheme is read from two other repositories |
| `TODS3` and `TODS9` are two numberings of the same project | **Consistent** — both prefixes are on one cartridge |
| `/menu/STAN.dat` is a leftover | **Verified** as unreferenced; **Open** as to what `STAN` means |
| The CG edition costs 4.79 MB less than the Anime edition | **Verified** — the budgets differ in the video row and nowhere else |
| Which edition was made first | **Open** — no date, stamp or structure orders them |

## The tools

Every number here is the output of a tool in [`tools/`](../tools), and every
tool's output is committed under [`reports/`](../reports), prefixed with the
edition it was run on. Python 3 standard library only, no dependencies.

Four of them were wrong before this cartridge was opened and are fixed here;
[07](07-compression.md) and [10](10-leftovers.md) say which, and
[99](99-open-questions.md) records what each failure would have cost.

Documentation only. No game asset, audio, graphic or code is committed.
