# The block codec

The question this cartridge was opened to answer: does the *Tales* block codec —
the 4,096-byte-ring LZSS with the nine-byte header that runs from *Tales of
Phantasia* (1995) to *Tales of Vesperia* (2008) — appear on a Nintendo DS
cartridge carrying the project number after *Vesperia*'s?

**It does not.** Four outcomes were possible and none was assumed; this page
gives the measurement, its denominators, and the step that had to happen first.

## Step zero, and this time it mattered

Section 7 of the corpus puts one thing before the scan on this platform:
decompress the modules, because `arm9.bin` and every overlay are normally
packed with `BLZ` and a scan over a packed module returns zero and is
indistinguishable from a clean negative.

**Thirty-two of the thirty-three modules on each cartridge are packed.**
1,620,780 bytes on the cartridge become 2,852,064 bytes of plaintext code. Two
previous DS pipelines ran this step and neither needed it; this one does, and
the decompressor that had never been exercised turned out to be wrong twice.
[04](04-executables.md).

Every figure below is over the plaintext.

## Pass 1 and pass 2: the constants

On ARM the scan is two scans, because the arithmetic splits the corpus's five
constants in half:

| Constant | Encodable as an ARM data-processing immediate? |
|---|---|
| 4070 (`0xFE6`) | **no** |
| 4071 (`0xFE7`) | **no** |
| **4078 (`0xFEE`)** | **no** |
| **4079 (`0xFEF`)** | **no** |
| 4080 (`0xFF0`) | **yes** — `0xFF ror #28` |

So the two constants the corpus calls the packer's cannot be written as ARM
immediates at all and reach the code as words in the literal pool, while the
2004 constant can. A single-pass scan sees at most one of them.

Both passes, over all 33 modules of the Anime edition
([`tools/ring_sites.py --arm --dir`](../tools/ring_sites.py),
[`reports/anime-ring-sites.txt`](../reports/anime-ring-sites.txt)):

| | ARM9 | ARM7 | 31 overlays | **total** |
|---|---:|---:|---:|---:|
| ARM data-processing immediates | 45,111 | 11,911 | 144,405 | **201,427** |
| THUMB instructions carrying a literal | 26,436 | 5,253 | 74,630 | **106,319** |
| 4-byte-aligned words | 186,366 | 39,882 | 486,768 | **713,016** |
| distinct PC-relative load targets | 7,175 | 1,800 | 18,158 | **27,133** |
| **4078 / 4079 / 4070 / 4071, either form** | **0** | **0** | **0** | **0** |
| 4080 | 3 immediates + 4 words | 0 | 0 | 7 |

The CG edition returns the same seven hits at the same addresses; its
immediate and literal counts differ by seven and eight respectively, which is
the regenerated secure area.

**The overlays are 71% of the ARM immediates and 70% of the THUMB literals.** A
scan of `arm9.bin` alone would have covered under a third of the code — the
same proportion *Tales of Innocence* recorded, and the reason
`ring_sites.py` now has a directory mode that prints a totals row.

## Every 4080 was read

Section 7 requires it, and on the two previous cartridges it was worth doing:
*Tales of the Tempest* had four of five `4080` immediates turn out to be entries
of a 4,096-scaled cosine table, and *Ratatosk no Kishi* had twelve alpha
counters and eight structure offsets. Here there are seven and they are three
kinds ([`reports/anime-4080-sites.txt`](../reports/anime-4080-sites.txt),
[`reports/anime-nearmiss.txt`](../reports/anime-nearmiss.txt)):

**1. A structure member's offset, immediately before a call.** `arm9 +0x081C3C`:

```
02081C34  bl      0x020213D4
02081C38  ldr     r1,[pc,#204]
02081C3C  add     r0,r4,#4080        <-- the hit
02081C40  str     r1,[r4,#3492]
02081C44  bl      0x020213D4
```

One of a run of `add r0,r4,#N` / `str r1,[r4,#M]` / `bl 0x020213D4` stanzas
with `N` = 808, 2912, 424, **4080**, 876 and on — one routine filling a large
structure member by member. The same shape as *Ratatosk no Kishi*'s eight.

**2. Half of the constant −16.** `arm9 +0x088C3C`:

```
02088C3C  add     r0,r5,#4080
02088C40  add     r0,r0,#61440
02088C44  mov     r0,r0,lsl #16
02088C48  mov     r0,r0,lsr #16
02088C4C  cmp     r0,#2
02088C50  bhi     0x02088CF0
```

`4080 + 61440 = 65520 = −16 mod 2**16`, so this is `if ((u16)(x − 16) <= 2)` —
a three-value range check, split across two immediates because ARM cannot
encode 65,520 in one. The constant is not 4080; it is an artefact of ARM's
immediate encoding, which is worth recording because it is a way for this
constant to appear that no other machine in the corpus offers.

**3. A four-field unpack of one word.** `arm9 +0x096298`:

```
02096290  and     r3,r1,#0xFF00000
02096294  and     lr,r1,#0xFF000
02096298  and     r12,r1,#4080        <-- 0xFF0
0209629C  cmp     r0,#7
020962A0  mov     r3,r3,lsr #20
020962A4  mov     r5,lr,lsr #12
020962A8  mov     lr,r12,lsr #4
020962AC  and     r12,r1,#15
```

This one deserves a sentence because it looks the most like the codec of
anything on either cartridge: it is a nibble-and-shift extraction, and the
codec's token is a nibble-and-shift extraction. It is not one. The masks are
`0xFF00000`, `0xFF000`, `0xFF0` and `0xF` with shifts of 20, 12, 4 and 0 — four
fields out of one 32-bit word, evenly spaced — where the codec splits a
*byte pair* into a 4-bit length and a 12-bit displacement. Four fields, not
two, and no ring anywhere near it.

**4–7. A 4,096-scaled cosine table, stored as data.** Four literal-pool words
equal to 4080, at `0x020A7088`, `0x020A70B0`, `0x020A74E8` and `0x020A7A60`,
and **not one of them is the target of any PC-relative load in the module**.
Reading the words around them:

```
… 4021 4034 4046 4056 4065 4074 4080 4086 4090 4094 4095 4096 4095 4094 4090 …
```

`round(4096 · cos θ)` for whole degrees, and `round(4096 · cos 5°) = 4080`.
The tool checks it rather than asserting it: **96 of 96 surrounding aligned
words** match a cosine run to within one.

This is *Tales of the Tempest*'s finding on a second cartridge in a different
form. There it was compiled as 446 eight-byte `mov r0,#K ; bx lr` stubs behind a
computed branch; here it is a plain array. `nearmiss.py` now tests for both
shapes, because the first form was the only one it knew and it scored zero on
the second.

## Pass 3: the structural probe

The constants can be computed, so the fingerprints are scanned for
independently ([`tools/struct_probe.py --dir`](../tools/struct_probe.py),
[`reports/anime-struct-probe.txt`](../reports/anime-struct-probe.txt)):

| Fingerprint | Total over 713,016 words |
|---|---:|
| `orr rX, rY, #0xFF00` — the control refill, **either spelling** | 8 |
| `lsl #20` then `lsr #20` — the ring mask | 2 |
| a literal-pool 4095 — the other form of the mask | 28 |
| `add`/`sub` on `sp` with a 4096..4400 immediate — a ring on the stack | 8 |
| `and #15` within eight instructions of an `lsr #4` | 6 |
| `add #19`, either instruction set | 67 |
| an `add #19` within 200 instructions of an `add #3` | 50 |
| **clusters of three or more distinct fingerprints within 200 instructions** | **0** |

Two rows have to be read rather than counted.

### The eight refills are not refills

`orr rX, rY, #0xFF00` is the fingerprint the corpus calls load-bearing — it is
how this format's decoders know when eight tokens are spent — and there are
eight of them here. All eight are in one 2 KB region of the ARM9 and all eight
look like this:

```
0205C8E0  cmp     r3,#255
0205C8E4  orrgt   r3,r3,#65280
0205C8E8  movgt   r3,r3,lsl #16
0205C8EC  movgt   r3,r3,asr #16
```

**They are sign extensions.** `if (x > 127) x |= 0xFF00;` followed by a
16-bit sign-extend is how a compiler widens a signed byte or a signed 9-bit
field to a halfword, and the routine they are in unpacks packed coordinate
pairs. Every one is *conditional* — `orrgt`, never `orr` — every one follows a
`cmp` against 127 or 255, and every one is followed by `lsl #16 ; asr #16`.
The codec's refill is unconditional and follows a byte load.

This is a correction the corpus needs, and [99](99-open-questions.md) states it
as one: **on ARM the refill fingerprint has a common innocent twin**, and the
discriminators are the condition code and the neighbouring `cmp`.

### The 67 `add #19` are the ARM/THUMB trap, for the third time

| | ARM `add #19` | THUMB `add #19` | THUMB hits inside an ARM word |
|---|---:|---:|---:|
| all 33 modules | **0** | 67 | **67** |

Not one genuine ARM `add #19` anywhere. All 67 are THUMB decodes of ARM code,
and in overlay 21 — which has 22 of them — the containing word is
`0xE1A03713`, `mov r3,r3,lsl r7`, or `0xE1B03513`, `movs r3,r3,lsl r5`.

That is the same idiom, with the same explanation, that *Tales of Innocence*
reported: the bit-consume step of the video decoder, repeated all through it.
Tempest found 24, Innocence 22, this cartridge 67, and the genuine ARM count is
zero on all three.

### And the probe's zero is weaker here than it was on PowerPC

`struct_probe.py` was calibrated on the 2003 GameCube build, where it finds 14
refills and 4 clusters — one per decoder copy — without being told where to
look. On the Xbox 360 it scored **zero refills on a build that plainly contains
two**, because Microsoft's compiler spells the refill with a separate
destination register; both spellings are counted here and were already counted
in the ARM version.

**But there is no ARM build in this corpus that contains this codec**, so the
zero above has no same-toolchain positive standing behind it. That is stated
rather than glossed, and two things are done about it instead of nothing: the
refill test does not require `rd == rn`, and `--selftest` hand-assembles every
fingerprint in every form the file looks for and checks that the detector
fires — 7 of 7 do. That demonstrates the detectors work. It does not
demonstrate that an ARM compiler would spell a real decoder the way they
expect, and it is printed at the top of the report so it is read before the
zero.

## Pass 4: the blind decode, per member and through the container

A blind decode over a whole image in one buffer is not the same test as a blind
decode over each of its members, because `plausible()` bounds a candidate by
the buffer it sits in. This cartridge nests five deep and one of the levels is
the executable, so the enumerator descends: `BLZ`-packed module → Nitro file
system → `FPS4` (with its `.b` / `.dat` split) → nested `FPS4` → `V154` → BIOS
stream → nine-byte block.

| | Anime | CG |
|---|---:|---:|
| payloads enumerated and swept | **47,195** | **47,195** |
| bytes | **376,083,362** | **376,083,366** |
| `BLZ` modules swept in plaintext | 33 | 33 |
| `FPS4` archives descended | 2,492 | 2,492 |
| `V154` objects descended | 1,508 | 1,508 |
| BIOS streams descended | 5,280 | 5,280 |
| archives that could **not** be read | 1 (`/m/misc/etc/tn.dat`) | 1 |
| **payloads that ARE a nine-byte block** | **0** | **0** |
| right header, wrong length | 0 | 0 |
| **blind-sweep survivors, both dialects, every offset** | **0** | **0** |
| **control: the 1995 cartridge, same invocation** | **1,089** | **1,089** |

[`reports/anime-census.txt`](../reports/anime-census.txt),
[`reports/cg-census.txt`](../reports/cg-census.txt).

Zero survivors is the expected noise floor here and it is worth saying why. On
the 4.29 GB Wii partition the same sweep produced ten chance survivors and they
had to be read; on a 256 MiB cartridge a four-byte needle has a chance rate of
0.0625, so zero is what a clean negative looks like rather than a suspiciously
round number.

## The strong test has no subject

The corpus's byte test — take *N* bytes of a known decoder and find the longest
identical run anywhere in the other image — needs a needle. There is no ARM
decoder for this codec in the corpus to take one from, and there is no decoder
on these cartridges to take one *of*.

Running it in the available direction measures the wrong thing: a PowerPC or
MIPS needle against an ARM image scores how much two instruction encodings
share, which is a fact about encodings. The corpus already records that
`VENUS.ELF` cannot be quoted against a non-MIPS needle for the same reason.

**So the strong test is unavailable, and that is the report.** What the
descent rests on instead is the constants, the structure, and 376 MB of blind
decode — which is what section 7 says to do when the directed measurement has
no denominator.

## Where this leaves the corpus

Two Nintendo DS cartridges in the corpus return this zero already, and both are
from studios outside the line. This is the third, and it is the first carrying
`TO9`. What it adds is stated with its condition attached in
[11](11-cross-title.md) and [99](99-open-questions.md): the cartridge does not
name its developer, so *the codec does not cross to this machine* and *the
codec did not cross with these hands* remain, on this evidence, a single
statement — narrowed by a project number and not closed by one.
