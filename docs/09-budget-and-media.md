# The budget, and the media

Two questions: how was every byte of the 256 MiB spent, and how much film and
sound is that. Both are answered twice, once per edition, because the
difference between the two answers *is* the answer to what the second edition
cost.

## Every byte, tessellated and checked

[`tools/formats.py --budget`](../tools/formats.py) lays the image out as
disjoint pieces — header, tables, modules, every file classified by its own
first bytes, the alignment slack between them, the tail — and then **checks
that the pieces sum to the image**, printing the discrepancy rather than
trusting the arithmetic. It is zero on both.

| | Anime | | CG | |
|---|---:|---:|---:|---:|
| container (`FPS4` / `V154`) | 99,635,302 | 37.12% | 99,635,302 | 37.12% |
| voice (CRI AHX) | 91,033,886 | 33.91% | 91,033,886 | 33.91% |
| **video (Mobiclip)** | **25,775,082** | **9.60%** | **20,988,934** | **7.82%** |
| music and effects (`SDAT`) | 21,146,560 | 7.88% | 21,146,560 | 7.88% |
| BIOS-format streams, whole files | 5,872,380 | 2.19% | 5,872,380 | 2.19% |
| unclassified files | 3,000,820 | 1.12% | 3,000,820 | 1.12% |
| the 31 overlays, `BLZ`-packed | 1,028,328 | 0.38% | 1,028,328 | 0.38% |
| ARM9, `BLZ`-packed | 432,924 | 0.16% | 432,920 | 0.16% |
| ARM7 | 159,528 | 0.06% | 159,528 | 0.06% |
| fonts | 141,916 | 0.05% | 141,916 | 0.05% |
| file name table | 42,281 | 0.02% | 42,281 | 0.02% |
| file allocation table | 41,160 | 0.02% | 41,160 | 0.02% |
| cartridge header | 16,384 | 0.01% | 16,384 | 0.01% |
| banner | 2,560 | — | 2,560 | — |
| a NitroSDK model | 2,420 | — | 2,420 | — |
| overlay table | 992 | — | 992 | — |
| alignment slack | 1,449,281 | 0.54% | 1,449,257 | 0.54% |
| **unused tail** | **18,648,412** | **6.95%** | **23,434,588** | **8.73%** |
| **sum** | **268,435,456** | **100.00%** | **268,435,456** | **100.00%** |
| **discrepancy** | **0** | | **0** | |

**Media share: 51.39% (Anime) and 49.61% (CG)** — voice plus video plus the
sound archive.

[`reports/anime-budget.txt`](../reports/anime-budget.txt),
[`reports/cg-budget.txt`](../reports/cg-budget.txt).

### Beside the corpus

| Build | Media share | Unused | Files |
|---|---:|---:|---:|
| *Tales of the Tempest*, DS 2006 | 13.22% | **41.3%** | 4,712 |
| *Tales of Innocence*, DS 2007 | 51.40% | 3.2% | 6,378 |
| *Ratatosk no Kishi*, Wii 2008 | 70.10% | — | 13,386 |
| *Tales of Vesperia*, Xbox 360 2008 | 30.84% | — | 162 (11,063 members) |
| **Hearts, Anime, DS 2008** | **51.39%** | **7.49%** | **5,145 (47,195 payloads)** |
| **Hearts, CG, DS 2008** | **49.61%** | **9.27%** | **5,145 (47,195 payloads)** |

The coincidence with *Innocence* — 51.39% against 51.40% — is a coincidence,
and the two get there differently: *Innocence* spends 2.81 hours on voice and
this cartridge spends 5.93.

### The unused space is unused

18.6 MB of tail sampling **one** distinct byte value, `0xFF`, over 4,194,304
bytes, deflating to **0.0974%** of itself. The alignment slack samples ten
values in its first mebibyte and 1,449,269 of them are `0xFF`.

That check exists because of *Tales of Vesperia*, where 19.08% of a disc looked
empty and turned out to be incompressible pseudo-random fill. Here it profiles
as free space, and neither cartridge is close to full.

## The video

Nine files, `MODS`, Actimagine Mobiclip — the same middleware *Tales of
Innocence* bought a year earlier, where *Tales of the Tempest* bought
Actimagine's older `VX`. The component tag names it: `[SDK+Actimagine:Mobiclip
SDK V1.0.2]`, and every file's version tag is `N3\n\0`.

| | Anime | CG |
|---|---:|---:|
| files | 9 | 9 |
| bytes | 25,775,032 | 20,988,896 |
| frames | **16,538** | **13,754** |
| duration | **13 m 33 s** | **11 m 32 s** |
| frame size | 256×192 on all nine | 256×192 on all nine |
| audio | 32,000 Hz, 2 channels on seven | 32,000 Hz, **1 channel on all nine** |

Per file, Anime edition:

| File | Bytes | Frames | fps | Duration |
|---|---:|---:|---:|---|
| `MOV000_A.mods` | 3,012,660 | 1,476 | 11.988 | 2 m 03 s |
| `MOV000_B.mods` | 1,730,588 | 1,476 | 11.988 | 2 m 03 s |
| `MOV001.mods` | 5,794,908 | 3,744 | 23.976 | 2 m 36 s |
| `MOV002.mods` | 2,627,964 | 1,704 | 23.976 | 1 m 11 s |
| `MOV003.mods` | 2,160,584 | 1,392 | 23.976 | 0 m 58 s |
| `MOV004.mods` | 1,755,000 | 1,056 | 23.976 | 0 m 44 s |
| `MOV005.mods` | 1,836,060 | 1,273 | 23.976 | 0 m 53 s |
| `MOV006.mods` | 2,948,400 | 1,921 | 23.976 | 1 m 20 s |
| `MOV007.mods` | 3,908,868 | 2,496 | 23.976 | 1 m 44 s |

### The frame rate is a field, not an assumption

A duration needs a frame rate and the corpus's rule is that nothing may be
estimated. The header states one, at `+0x14`, as a `u32` in 8.24 fixed point:

```
0x17F9DB23 / 2**24 = 23.9760      = 24000/1001, the NTSC film rate
0x0BFCED91 / 2**24 = 11.9880      = exactly half of it
```

Seven files carry the first and two carry the second, and the two are
`MOV000_A` and `MOV000_B`, the two halves of one opening. That the field is a
rate rather than an arbitrary constant is settled by three things at once: it
lands on a standard rate to four decimal places, the second value is exactly
half the first, and the two files carrying the half are the pair that also
share a frame count.

`MOV000_B` is the only file on either cartridge with a zero in **both** audio
fields — it is the silent half of a two-screen opening.

## The voice

4,456 files under `/s`, none with an extension, all of them **CRI AHX** — the
encoding byte at `+4` reads `0x11`, and `(c)CRI` sits in every header:

| | |
|---|---:|
| files | **4,456** |
| bytes | 91,033,886 |
| **duration** | **5 h 56 m 01 s** |
| 16,364 Hz, mono | 2,959 files |
| 12,273 Hz, mono | 1,497 files |

Beside them, `/s/lvd` holds 518 tiny files, one per voice line, which the ARM9
loads with the format string `s/lvd/%s.lvd`.

## The music and the effects

One 21 MB `SDAT`, the NitroSDK sound archive, with its symbol block **on** — so
every record is named ([`tools/sdat.py`](../tools/sdat.py)):

| Table | Entries | Named |
|---|---:|---:|
| `SEQ` | 60 | 60 |
| `SEQARC` | 192 | 192 |
| `BANK` | 293 | 254 |
| `WAVEARC` | 3 | 3 |
| `PLAYER` | 11 | 11 |
| `GROUP` | 282 | 195 |
| `PLAYER2` | 3 | 3 |
| `STRM` | 27 | 27 |

532 members: 254 `SBNK`, 188 `SSAR`, 60 `SSEQ`, 27 `STRM`, 3 `SWAR`.

| | |
|---|---:|
| streamed music (`STRM`, 27 members) | **36 m 32 s** |
| sampled waves (`SWAV`, 672 records in 3 `SWAR`) | 5 m 43 s |
| records this reader could not parse | **1**, named in the report |

The sequence names are plain: `MUS_B000`, `MUS_D001`, `MUS_E004`, `MUS_T007`,
`MUS_I000` — battle, dungeon, event, town, and so on.

The `STRM` sample rate is identified rather than asserted: the field beside it
satisfies `period == 0x1000000 / (rate * 32)` on all 27 records, which is what
a rate and its timer reload look like together. Three rates occur — 16,364,
22,767 and 52,365 Hz — and the third is above the recommended DS maximum of
32,768 while remaining reachable by a timer-driven channel, so it is reported
as the file states it.

## Total

| | Anime | CG |
|---|---:|---:|
| video | 13 m 33 s | 11 m 32 s |
| voice | 5 h 56 m 01 s | 5 h 56 m 01 s |
| streamed music | 36 m 32 s | 36 m 32 s |
| sampled waves | 5 m 43 s | 5 m 43 s |
| **total sound** | **6 h 38 m 16 s** | **6 h 38 m 16 s** |

Against *Tales of Innocence*'s 2.81 hours of voice and *Ratatosk no Kishi*'s
17 h 42 m of audio and 20 m 23 s of video, and *Tales of Vesperia*'s 6 h 22 m.

[`reports/anime-media.txt`](../reports/anime-media.txt),
[`reports/cg-media.txt`](../reports/cg-media.txt),
[`reports/anime-sdat.txt`](../reports/anime-sdat.txt),
[`reports/anime-sdat-names.txt`](../reports/anime-sdat-names.txt).
