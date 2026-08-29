# The executables, and the step that had to come first

Section 7 of the corpus makes one thing the first act on a Nintendo DS: get the
modules into plaintext, because `arm9.bin` and every overlay are normally
packed with `BLZ`, the linker's backwards LZ, and **a constant scan over a
packed module returns zero and is indistinguishable from a clean negative**.

Two DS cartridges had already been opened and neither had exercised it.
*Tales of the Tempest* has no overlays and both its modules are stored plain;
*Tales of Innocence* has three overlays and all three are stored plain. The
corpus recorded that honestly: *"this step has still never prevented a false
negative, and the only reason that is known is that it was run every time."*

**On these two cartridges it prevents one.**

## Thirty-two of thirty-three

| | |
|---|---:|
| modules | 33 — ARM9, ARM7, 31 ARM9 overlays |
| `BLZ`-packed | **32** — the ARM9 and all 31 overlays |
| not packed | 1 — the ARM7 |
| bytes on the cartridge | 1,620,780 |
| bytes of plaintext code | **2,852,064** |

[`reports/anime-modules.txt`](../reports/anime-modules.txt),
[`tools/ndsmodules.py`](../tools/ndsmodules.py).

Swept as shipped, that is 1.6 MB of LZSS output in which nothing parses. Every
number on [06](06-the-codec.md) would have been drawn from a denominator that
was 43% smaller and made of the wrong bytes, and the answer would have looked
exactly the same.

## Three independent statements, and all three are printed

The tool does not trust one source for whether a module is packed:

* **the overlay table** carries a per-overlay `compressed` flag and a 24-bit
  packed length — all 31 say yes;
* **the module parameters** carry `compressed_static_end`, and it reads
  `0x02069B1C`, which is `arm9_ram + arm9_size` exactly, so the ARM9's packed
  image ends where the ARM9 ends;
* **the `BLZ` footer**, eight bytes at the end of each module, which can be
  validated by decompressing and which nobody had to keep up to date.

The module parameters were located by their own magic pair — `nitro_code_be`
`0xDEC00621` followed by `nitro_code_le` `0x2106C0DE` — at file `+0xBBC`, so
the struct begins at `+0xBA0`:

```
+0x00  autoload_list        0x020B5FE0 .. 0x020B5FF8
+0x08  autoload_start       0x020B5C60
+0x0C  static_bss           0x020B5C60 .. 0x0213A4E0
+0x14  compressed_static_end 0x02069B1C   (arm9_ram + arm9_size = 0x02069B1C)
+0x18  sdk_version          0x04027531
```

## The corpus's `BLZ` decompressor was wrong, twice

It had never been executed. Written for *Tales of the Tempest*, which has no
overlays; carried to *Tales of Innocence*, whose three overlays are stored
plain; run here for the first time on a module that is actually packed, it
failed on all thirty-two.

Two defects, and both fail in a way that reads like the module simply not being
packed:

* **the two bytes of a match token were assembled in the wrong order.** The
  stream is written backwards, so walking backwards the byte at the *higher*
  address is the one a forward reader sees first and is therefore the high half
  of the token. Reversed, the displacement comes out enormous and the decode
  either throws or produces rubbish.
* **the copy was not clamped to the end of the encoded region**, so a match
  running past it corrupted the verbatim prefix instead of being truncated the
  way the reference implementation truncates it.

## And there is a positive control for the fix, on the cartridge itself

This is what makes the repair checkable rather than plausible. **The overlay
table states each overlay's plaintext length**, in its `ram_size` field, which
is written by the Nintendo linker and not by any tool here. So:

> **31 of 31 overlays decompress to exactly their declared length.**

Thirty-one independent numbers, produced by the linker, matched by the
decompressor. A defect that survived two pipelines is closed by a control that
was on the cartridge the whole time.

The ARM9 has no such field, so it is checked differently: its footer states a
length delta of 312,540 and `432,924 + 312,540 = 745,464`, which is what comes
out, and the plaintext begins at the ARM9 entry point with
`mov r12,#0x4000000 ; str r12,[r12,#520]` — the NitroSDK's first instruction.

## The secure area

The first 2 KiB of the ARM9 is the NitroSDK's secure area, and it does not
disassemble. Its entropy is **7.866 bits** over 2,048 bytes with **256 of 256**
distinct byte values, and the header's own secure-area CRC does not recompute
under any of the three plausible reconstructions.

That reads exactly like ciphertext, and it is not. The measurement that decides
it is a control ([`tools/securearea.py`](../tools/securearea.py)):

| | `svc #N ; bx lr` pairs |
|---|---:|
| the 2,048-byte secure area | **17** |
| 5,793,792 bytes of Mobiclip video, 2,829 windows of the same size | **0** |

Seventeen well-formed THUMB system-call wrappers — `DF 12 47 70` is
`svc #0x12 ; bx lr` — embedded in filler, where a comparable volume of
high-entropy data contains none. It is readable code in generated padding, and
the padding is regenerated per build: the same seventeen services sit at
different addresses on the two cartridges. [02](02-the-two-editions.md).

That matters for [07](07-compression.md), because **the BIOS decompression
wrappers live in there**, and a caller census that could not locate them would
be measuring nothing.

## What the modules say about the build

| | |
|---|---|
| C++ names in 2,852,064 bytes of plaintext | **5**, and all five are the standard library's: `std::bad_exception`, `std::exception`, `std::length_error`, `std::logic_error`, `tree::insert` |
| application class names | **0** |
| RTTI | **off** |
| exception support | linked — the five names are a runtime diagnostic table, separated by `!` |
| `__DATE__` | **`Nov 19 2008`**, once, in overlay 1 |
| SDK component tags | 2 |
| CRI middleware version strings | 8, all stamped `Aug 26 2008` |

The zero in the second row is the one that shapes [05](05-who-made-it.md): with
RTTI off there is no class-name list, so several questions this corpus normally
answers from one are unanswerable here, and that is a property of the build
settings rather than of the studio. *Tales of Innocence* has 1,047 class names,
*Tales of Vesperia* 445, *Ratatosk no Kishi* 0. This is the third case.

And there is no symbol table either: `symbols.py` finds **18 length-prefixed
type names over all 33 images**, nine of them under one identifier (`hd`) in
overlay 0 and two under another (`F00`) in overlay 1 — no RTTI records, no
demangled classes, nothing that names a framework. *Tales of Innocence*'s
equivalent figure is 1,047.

[`reports/anime-classnames.txt`](../reports/anime-classnames.txt),
[`reports/anime-symbols.txt`](../reports/anime-symbols.txt),
[`reports/anime-leftovers.txt`](../reports/anime-leftovers.txt).
