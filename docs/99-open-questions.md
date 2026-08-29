# Open questions

Everything here is stated with the measurement beside it. An open question with
no number attached is an opinion.

## 1. Who built these cartridges

**Open, and it is the question that conditions the rest of the repository.**

The corpus needs a Nintendo DS title from the studio line that carried the
block codec from 1995 to 2005, because the two DS cartridges it already has are
from studios outside it and their two zeros are compatible with two different
readings. Whether these cartridges are that title is not answerable from these
bytes.

What is measured:

* the developer is named **nowhere**, in ASCII, Shift-JIS or UTF-16LE, over
  271,287,520 bytes: `テイルズスタジオ` 0, `株式会社` 0, `ウルフチーム` 0,
  `アルファ・システム` 0, `Dimps` 0;
* the build was compiled with **RTTI off** — 5 C++ names in 2,852,064 bytes of
  plaintext code and all five are the standard library's — so there is no
  class-name list, which is where *Tales of Innocence* named its studio's
  framework and *Tales of Vesperia* named both companies;
* the publisher is named once, in the banner, in UTF-16;
* the project tag **`TO9`** is in six file names, in a file extension used by
  101 container members, and in a debug overlay's version banner;
* `TO7` is *Tales of the Abyss*'s tag and `TO8` is *Tales of Vesperia*'s,
  **read from two other repositories in this corpus**, not from these images.

What would settle it: a credits screen that is text rather than graphics, a
build with RTTI on, or a source path. None of the three is here.

**Verified**: the string `TO9` is on both cartridges in those three roles.
**Consistent**: that it is the next number in the line's own scheme.
**Open**: whose hands held it.

## 2. What `STAN` is

**Open.** `/menu/STAN.dat` is an eighth 25,900-byte entry in a seven-entry
family of party-portrait archives, structurally identical to its siblings, with
its own artwork rather than a copy of one of them, and **named by none of the
33 plaintext modules** on either cartridge while all seven siblings are named
twice in overlay 20.

Three readings survive:

1. *Tales of Destiny*'s 1997 protagonist, left in the family as a placeholder
   or a cut cameo;
2. an abbreviation of something unrelated;
3. an eighth entity cut for other reasons.

**What narrows the corpus's own question**: `dimlos` returns **0**, and
ディムロス returns 0. *Tales of the Tempest* raised `stan` and `dimlos` as a
pair and the pairing is what made the placeholder reading fit there. Three DS
cartridges now, and the pair occurs on one of them.

Measuring the artwork would settle at least reading 2, and this repository does
not do it: the six `.NCBR` banks are game graphics and decoding them to look at
them is outside what a documentation-only repository publishes.

## 3. Which edition was made first

**Open, and the checks are worth listing because they all came back empty.**

The only compiler stamp on either cartridge is `Nov 19 2008`, in overlay 1, and
overlay 1 is byte-identical between the two. The eight CRI middleware stamps
read `Aug 26 2008 16:33:56`–`16:34:03` on both. A DS file allocation table has
no timestamp field, the header has no date, the banner has none, and the only
structure that is regenerated per build — the secure-area filler — carries no
ordering.

The 4-byte difference in packed ARM9 length and the different game codes order
nothing.

## 4. Where the software LZ77 and LZ11 decoder is

**Open.** The cartridge holds 5,280 BIOS-format streams that decode and consume
themselves exactly, 61,737,814 bytes becoming 123,245,746, and **zero callers**
of any of the six linked decompression wrappers over 43,946 resolved branch
targets, in either instruction set, across the module boundary, with no wrapper
address occurring as a data word.

So the routine is in the image and `lzprobe.py` did not find it. Its
co-location counts — 66 THUMB `lsr #12` sites within 40 instructions of a `+3`
in the ARM9, 16 in the largest overlay — are noise at those denominators, and
no site carries enough fingerprints together to name a routine.

This is the second time the probe has failed on a cartridge that demonstrably
contains its target; *Tales of Innocence* was the first. Two failures on two
different builds is now a fact about the probe rather than about either
cartridge.

## 5. Why the container crossed and the codec did not

**Open, and it is the sharpest thing these cartridges hand the corpus.**

`FPS4` is on the Xbox 360 *Tales of Vesperia* disc, mastered 2008-06-20, with a
0x1C header, a field mask selecting which of four per-entry fields exist, and
32-byte names. It is on these cartridges, built 2008-11-19, with the same
header, the same mask semantics and the same names — and little-endian instead
of big-endian.

The codec is on that disc and is not on these. So on this pair the container's
structure crossed a change of machine, of byte order and of processor family in
five months, and the compressor it holds did not.

The corpus's shape after *Vesperia* was *the codec persists and the packer
varies*. This adds a third thing that persists — the container — and gives it
the same behaviour as the block header: **a structure that travels and lets the
machine choose its byte order.** What it does not say is why one of the two
travelled and the other did not.

## 6. What `TODS3` and `TODS9` are, when both are on one cartridge

**Consistent, not verified.** Ten root data files are `TODS3_*`, four shop
tables are `CTODS3_*`, six item tables are `TODS9_*`, six battle tables are
`To9_*`, 101 container members end `.to9moh`, and 1,472 end `.ds3`.

The reading that fits all of them without either number being wrong is that
this build carries two numberings at once — the third *Tales* on this machine
and the ninth project of the line — and that `.ds3` is the first of the two.
Nothing on the cartridge confirms either expansion.

## 7. What `V154` is a version of

**Open.** The tag is literally `V154`, the header is 0x6C bytes, and `+0x14`
plus `+0x18` equals the object's own length on every standalone instance. The
four-character tag reads like a version number and no string on either
cartridge expands it. 1,508 objects and 19 files, all of them behind the
project's own `.ds3` extension.

## 8. What `/m/misc/etc/tn.dat` is

**Open, and named rather than skipped.** 188,416 bytes, first four bytes
`FPS4`, and its entry table does not resolve against itself or against any
sibling under either of the three field masks seen elsewhere. It is the one
archive of 2,493 the reader cannot open. It was swept as a single opaque
payload, so the blind decode covers its bytes; it is not descended into, so its
members are not separately bounded.

## 9. What the eight `orr rX,rY,#0xFF00` sites mean for the corpus's probe

**Answered here, and it is a correction section 7 should carry.**

The control-register refill is the fingerprint the corpus calls load-bearing.
On ARM it has a common innocent twin: a compiler widening a signed byte or
signed 9-bit field to a halfword emits

```
cmp    rX, #127        (or #255)
orrgt  rX, rX, #0xFF00
movgt  rX, rX, lsl #16
movgt  rX, rX, asr #16
```

and this cartridge carries eight of them in one routine that unpacks packed
coordinate pairs. The discriminators are **the condition code** — the codec's
refill is unconditional — and **the neighbouring `cmp`**, which the codec does
not have because its refill follows a byte load.

A probe that counts `orr rX,rY,#0xFF00` without them reports eight refills on a
build with none.

## 10. There is no ARM positive control for the structural probe

**Open, and structural.** `struct_probe.py` was calibrated on the 2003 GameCube
build, where it finds 14 refills and 4 clusters without being told where to
look, and the Xbox 360 build showed what happens when a new toolchain spells a
fingerprint differently: it scored **zero refills on a build that plainly
contains two**.

**No ARM build carrying this codec is known to exist**, so the zero on these
cartridges has no same-toolchain positive behind it. Two things were done about
it instead of nothing: the refill test does not require `rd == rn`, and
`--selftest` hand-assembles each fingerprint in each form the file looks for
and checks the detector fires — 7 of 7 do.

That demonstrates the detectors work. It does not demonstrate that an ARM
compiler would spell a real decoder the way they expect, and the report prints
that sentence above the numbers.

The corresponding gap on the byte side is worse and is stated in
[06](06-the-codec.md): **the strong test has no subject.** There is no ARM
decoder in the corpus to take a needle from, so `prefix_scan.py` was not run —
running it with a PowerPC or MIPS needle would measure how much two instruction
encodings share.

## 11. What would change these answers

| Question | What would settle it |
|---|---|
| who built it | a build from this line with RTTI on, or a text credits file |
| the strong byte test | any ARM build in the corpus that contains the codec |
| the structural probe's calibration | the same |
| the software LZ decoder | a disassembly pass rather than a fingerprint scan |
| `STAN` | rendering six `.NCBR` banks, which this repository does not publish |
| edition order | a second dump, a manual, or anything outside the images |
| `V154` | any other title using the same tag |

## 12. What the corpus's next target is

The codec's last confirmed appearance is *Tales of Vesperia*, 2008-06-19. These
cartridges are five months later and do not carry it, from a project numbered
one after *Vesperia*'s — but by a team these images do not name.

The places the corpus has named and not yet opened remain the 2005 PSP port of
*Eternia*, the 2006 PlayStation 2 remake of *Destiny*, *Radiant Mythology*
(PSP, 2006) and the 2009 PlayStation 3 port of *Vesperia*. To that list these
cartridges add one more, and it is the one that would decide question 1: **any
title carrying `TO9` on another platform**, or any build from this line with
its class names left in.
