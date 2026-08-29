# The two editions

*Tales of Hearts* shipped as two cartridges on one day: an **Anime Movie
Edition** (`CTUJ`) and a **CG Movie Edition** (`CTGJ`). Nothing else in this
corpus has that shape, and it supplies a control that costs nothing to run:
everything identical between the two is the game, and everything that differs
is the edition.

This page is that measurement. It is placed second because every other page
depends on it — once the two images are shown to be one build, a result
measured on one is a result about both, and the repetition of every probe on
the second cartridge becomes a check rather than a separate finding.

## The comparison

Both images were enumerated with the same container descent
([`tools/census.py`](../tools/census.py)) and compared payload by payload by
SHA-1 ([`tools/crosstitle.py`](../tools/crosstitle.py)):

| | Anime | CG |
|---|---:|---:|
| payloads enumerated | 47,195 | 47,195 |
| distinct payloads | 28,679 | 28,679 |
| bytes | 376,083,362 | 376,083,366 |
| **byte-identical between them** | **28,662 of 28,679** | |
| distinct internal names | 29,778 | 29,778 |
| **names present on one side only** | **0** | |

[`reports/variants-crosstitle.txt`](../reports/variants-crosstitle.txt).

The name lists are identical because the file name table is identical: both
cartridges carry a 42,281-byte `FNT` and a 41,160-byte `FAT` at the same
offsets, so the two file systems have the same 5,114 names in the same order.
Only the *contents* and the *extents* differ.

## The seventeen

Every payload that is not byte-identical, and why:

| Payload | Why it differs |
|---|---|
| `/movie/MOV000_A.mods` … `MOV007.mods` (9 files) | **the edition** |
| `/movie/memo.txt` | 50 bytes of Shift-JIS naming which edition this is |
| `[ROM header 0x0]` | game code, title, declared size, both CRCs |
| `[banner]` | `アニメムービーエディション` against `CGムービーエディション` |
| `[FAT]` | every file after `/movie/` starts at a different offset |
| `[header slack 0x200]`, `[gap 0x6DB1C]` | alignment around the modules |
| `[tail 0xEE372A4]` | 18,648,412 bytes of `0xFF` against 23,434,588 |
| `[module arm9, BLZ plaintext]` | see below |

Seventeen, and there is no eighteenth. The 31 overlays, the ARM7, all 75
containers, all 4,456 voice files, the sound archive, the fonts and every
member inside every archive are byte for byte the same on both cartridges.

## `/movie/memo.txt`

Fifty bytes, in Shift-JIS, in the movie directory, on both cartridges:

```
Anime:  Info : 現在のデータはアニメーションムービーです
CG:     Info : 現在のデータはCGムービーです
```

*"the current data is the animation movie"* / *"…is the CG movie"*. It is a
note to whoever was running the build, it is not referenced by any module, and
it shipped twice.

## The one executable difference

`arm9.bin` decompresses to **745,464 bytes on both cartridges** and the two
plaintexts differ in **2,045 bytes across 21 runs**. Every run is one of three
things:

**1. The secure area, 0x0E to 0x7FE.** A DS cartridge's first 2 KiB of ARM9 is
the NitroSDK's secure area: seventeen `svc #N ; bx lr` THUMB wrappers embedded
in high-entropy filler. The filler is regenerated per build and the wrappers
land at different addresses — the same seventeen services, in a different
order:

```
Anime   0x020000DC svc #0x12   0x0200013A svc #0x14   ...  0x020007A2 svc #0x03
CG      0x02000082 svc #0x0C   0x020000EE svc #0x0B   ...  0x020007A4 svc #0x03
```

That this is code and not ciphertext is a measurement rather than an
assumption: 2,048 bytes containing seventeen well-formed wrappers, against
**zero** in 5,793,792 bytes of Mobiclip video used as a control
([`tools/securearea.py`](../tools/securearea.py)).

**2. Eight `BLX` offsets, at exactly eight addresses.** Because the wrappers
moved, every call to one moved with it:

```
0x0206B958  0x0206BB8C  0x0206BBF0  0x0206BEA8
0x0206D6EC  0x02072374  0x02072420  0x02074234
```

Those eight addresses are **exactly** the eight call sites
[`tools/bios_calls.py`](../tools/bios_calls.py) reports independently — one
`CpuSet` and seven `Stop/Sleep` — found by resolving 43,946 branch targets
without being told where to look. Two tools, two questions, one list of eight
addresses. [07](07-compression.md).

**3. One byte at `+0x0BB4`.** `compressed_static_end` in the module
parameters: `0x02069B1C` against `0x02069B18`, which is the packed ARM9's own
length, and the packed lengths are 432,924 and 432,920.

There is no fourth kind. **The two cartridges run the same code.**

## What the edition costs

The budgets ([`tools/formats.py --budget`](../tools/formats.py)) differ in one
row:

| | Anime | CG | difference |
|---|---:|---:|---:|
| container (`FPS4` / `V154`) | 99,635,302 | 99,635,302 | 0 |
| voice (CRI AHX) | 91,033,886 | 91,033,886 | 0 |
| music and effects (`SDAT`) | 21,146,560 | 21,146,560 | 0 |
| **video (Mobiclip)** | **25,775,082** | **20,988,934** | **−4,786,148** |
| BIOS-format streams | 5,872,380 | 5,872,380 | 0 |
| executables | 1,620,780 | 1,620,776 | −4 |
| unused tail | 18,648,412 | 23,434,588 | +4,786,176 |
| **media share of the cartridge** | **51.39%** | **49.61%** | |

So the answer to *what does the CG edition cost* is that it costs **less**:
4.79 MB less, and the saved space is left as `0xFF`. Both cartridges are the
same 256 MiB part and neither is close to full.

## And the two are different films, not one film re-encoded

Read from the Mobiclip headers
([`tools/media_census.py`](../tools/media_census.py)):

| | Anime | CG |
|---|---:|---:|
| files | 9 | 9 |
| total frames | **16,538** | **13,754** |
| total duration | **13 m 33 s** | **11 m 32 s** |
| audio channels | 2 on seven files, 1 on two | **1 on all nine** |
| frame rate | 23.976 on seven, 11.988 on two | the same split |
| frame size | 256×192 on all | 256×192 on all |

Not one of the nine has the same frame count in both editions, and the
per-file differences do not share a sign — `MOV001` is *longer* in the CG
edition (3,894 frames against 3,744) while `MOV002` is less than half as long
(750 against 1,704). Two separately cut and separately encoded sets, not one
source at two bitrates. The CG edition also drops to mono throughout, which
the Anime edition does on only two of its nine.

The frame rate is not assumed. It is a field: a `u32` at `+0x14` in 8.24 fixed
point, `0x17F9DB23 / 2**24 = 23.9760` — which is 24000/1001, the NTSC film
rate — and `0x0BFCED91 / 2**24 = 11.9880`, exactly half of it, on the two
halves of the opening. [09](09-budget-and-media.md).

## Which came first

**Open, and it is worth saying what was checked.** The only compiler date on
either cartridge is `Nov 19 2008`, in overlay 1, and overlay 1 is byte-identical
between the two. The eight CRI middleware stamps read `Aug 26 2008` on both.
The banner, the header and the file name table carry no timestamp; the DS file
allocation table has no date field; and the one structure that *is* regenerated
per build — the secure area filler — is not ordered.

Nothing on either cartridge places one before the other.
