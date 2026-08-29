# nds-talesofhearts-doc

Byte-level documentation of ***Tales of Hearts*** (Nintendo DS, Namco Bandai
Games, 18 December 2008, Japan) — **both cartridges**: the Anime Movie Edition
(`CTUJ`) and the CG Movie Edition (`CTGJ`).

Documentation only. No game asset, audio, graphic or code is committed. Every
number here is the output of a tool in [`tools/`](tools), and every tool's
output is committed under [`reports/`](reports), prefixed with the edition it
was run on. Python 3 standard library, no dependencies.

This is the fifteenth build in the [*Tales* block codec
corpus](https://github.com/vs-sr-dev/tales-blockcodec-doc) and the third
Nintendo DS cartridge in it.

---

## Highlights

**Two cartridges, one build.** *Tales of Hearts* shipped twice on one day, and
running the identical container descent over both gives the control the corpus
has never had on a cartridge: **28,662 of 28,679 distinct payloads are
byte-identical**. Seventeen differ and every one is the film or a structure
that moves because of it — the nine movies, a 50-byte build note, the header,
the banner, the file allocation table, two alignment regions, the tail, and
`arm9.bin`, whose plaintext differs only in regenerated secure-area filler,
eight `BLX` offsets into it, and one byte of its own packed length.

**The block codec is not here, and step zero is why that is worth saying.**
**Thirty-two of the thirty-three executable modules are `BLZ`-packed** — the
ARM9 and all thirty-one overlays — so 1,620,780 bytes on the cartridge become
2,852,064 bytes of plaintext code, and a scan of the shipped image would have
returned the same zero over the wrong bytes. Two previous DS pipelines ran this
step and neither needed it. Over the plaintext: **0** of `4078` / `4079` /
`4070` / `4071` in either ARM encoding, out of **201,427** ARM data-processing
immediates, **106,319** THUMB literals, **713,016** aligned words and
**27,133** distinct PC-relative load targets. All seven `4080` sites were
disassembled: a structure offset before a call, half of the constant −16 in a
range check, a four-field unpack of one word, and four unreferenced words
inside a table where **96 of 96 surrounding aligned words are
`round(4096 · cos θ)` to within one**.

**And the corpus's `BLZ` decompressor was wrong, twice, and had never been
run.** Written for a cartridge with no overlays and carried to one whose three
overlays were stored plain, it assembled a match token's two bytes in the wrong
order and did not clamp the copy to the end of the encoded region. Both fail in
the direction of *this module is not packed*. The fix has a positive control
that was on the cartridge the whole time: the overlay table states each
overlay's plaintext length, and **31 of 31 overlays decompress to exactly their
declared length**.

**`FPS4` crossed and the codec did not.** The container on these cartridges is
the container on the Xbox 360 *Tales of Vesperia* disc mastered five months
earlier — same 0x1C header, same field mask selecting which of four per-entry
fields exist, same 32-byte names — **little-endian here and big-endian there**.
The byte order is the machine's and the structure is the line's, which is the
nine-byte block header's behaviour in reverse. 2,492 archives read against
2,493 magic hits.

**A third field-mask trap, failing the other way.** *Vesperia* recorded a
reader that assumes one entry layout misreading another *towards huge sizes*.
Here a mask of `0x0001` states offsets and no sizes — the members run to the
next offset — and a reader requiring an explicit size reports **no members at
all**: 1,904 nested archives were reported unreadable before the reader learned
the implicit form. That failure points at a clean-looking zero, which makes it
the more dangerous of the two on a census.

**The data is in the platform's formats and the platform's code never runs.**
**5,280** BIOS streams inside the containers, **61,737,814 → 123,245,746**
bytes, 4,034 `LZ77` and 1,246 `LZ11` — against **zero callers** of all six
linked decompression wrappers over **43,946** resolved branch targets, across
the module boundary, with `CpuSet` at one caller and `Stop/Sleep` at seven so
the instrument is shown to find callers where there are callers. Those eight
call sites are, independently, the eight addresses at which the two editions'
executables differ.

**The blind decode.** **0 blocks in 47,195 payloads and 376,083,362 bytes**,
both dialects, at every offset, on each cartridge — against the 1995
cartridge's **1,089** returned by the same unmodified decoder in the same
invocation.

**But the cartridge does not name its developer.** Zero company strings in
ASCII, Shift-JIS *and* UTF-16LE; RTTI compiled off, so **5 C++ names in
2,852,064 bytes and all five are the standard library's**. What is there is a
project number: **`TO9`**, in six file names, in a file extension of its own
(`.to9moh`, 101 members) and in a debug overlay's version banner four bytes from
its build date — the next number after `TO7` (*Abyss*, 2005) and `TO8`
(*Vesperia*, 2008). That is the whole of the lineage evidence and every page
here carries the condition.

**The SDK component list is not the licence list.** Two `[SDK+…]` tags —
`NINTENDO:BACKUP` and `Actimagine:Mobiclip SDK V1.0.2` — beside **eight CRI
components** that name and date themselves in the ARM9, a CRI file-system
layer, CRI's entire error table, and `(c)CRI` **8,912 times**. *Tales of
Innocence* licensed nine CRI components and tagged them; this build licensed
eight and tagged none.

**Nothing crossed at the asset level, in any direction.** 0 shared names of
29,778 against *Innocence*'s 4,959, *Tempest*'s 4,712 and *Vesperia*'s 162; the
two byte-identical payloads are two bytes of `0x00` and four bytes of `0xFF`
and are read and dismissed. Every other title's cast returns **0** across
56,324 internal names while this cartridge's own returns 194, 159, 131, 129,
125 and 105.

**One leftover that the corpus has been waiting on.** `/menu/STAN.dat` is an
**eighth 25,900-byte entry in a seven-entry family of party portraits**, with
its own artwork, which **no module names** — while overlay 20 names all seven
siblings twice. `dimlos` returns **0**. *Tales of the Tempest* raised `stan`
and `dimlos` as a pair; three DS cartridges in, the pair occurs on one of them.

**What the second edition cost: less.** The two budgets differ in one row. The
CG edition's nine films are **4,786,148 bytes smaller**, 13,754 frames against
16,538, 11 m 32 s against 13 m 33 s, and mono on all nine where the Anime
edition is stereo on seven. The saved space is left as `0xFF`.

---

## Status of every claim

| Claim | Status | Evidence |
|---|---|---|
| The block codec is absent from both cartridges | **Verified** | 201,427 + 106,319 + 713,016 + 27,133 denominators; 0 blocks in 376,083,362 bytes; control returns 1,089 in the same run |
| All seven `4080` sites are innocent | **Verified** | each disassembled; 96 of 96 words around the four literal hits are `round(4096·cos θ)` |
| The genuine ARM `add #19` count is zero | **Verified** | 0 ARM, 67 THUMB, all 67 inside ARM words — the third cartridge to show it |
| Thirty-two of thirty-three modules are `BLZ`-packed | **Verified** | overlay flags, module parameters and `BLZ` footers agree; 31 of 31 decompress to their declared length |
| The container is `FPS4`, little-endian, with *Vesperia*'s field-mask semantics | **Verified** | 2,492 archives read, 2,493 magic hits, three masks |
| The build calls no BIOS decompression service | **Verified** | 0 of 6 over 43,946 branch targets; `CpuSet` 1, `Stop/Sleep` 7 |
| The data is nonetheless in BIOS formats | **Verified** | 5,280 streams, 61,737,814 → 123,245,746 |
| The two editions are one build with one asset group swapped | **Verified** | 28,662 of 28,679 payloads identical; all 17 differences located |
| The cartridge does not name its developer | **Verified** | zero in ASCII, Shift-JIS and UTF-16LE over 271,287,520 bytes |
| RTTI is off | **Verified** | 5 C++ names in 2,852,064 bytes, all standard library |
| The budget tessellates the image exactly | **Verified** | discrepancy 0 on both |
| The unused space is free space | **Verified** | one byte value, deflates to 0.0974% |
| The CG edition is 4,786,148 bytes cheaper | **Verified** | the budgets differ in the video row and nowhere else |
| Nothing crossed from any other title | **Verified** | 0 shared names against three neighbours; two coincidences read |
| `/menu/STAN.dat` is unreferenced | **Verified** | `STAN` absent from all 33 modules; its seven siblings named twice each |
| `TO9` is this project's tag in the scheme of `TO7` and `TO8` | **Consistent** | the string is in these bytes; the scheme is read from two other repositories |
| `TODS3` and `TODS9` are two numberings of one project | **Consistent** | both prefixes on one image, on different tables |
| What `STAN` means | **Open** | three readings; `dimlos` returns 0 |
| Which edition was made first | **Open** | no date, stamp or structure orders them |
| Where the software `LZ77`/`LZ11` decoder is | **Open** | `lzprobe.py` returns co-locations that are noise at their denominators |
| Whether an ARM structural zero is trustworthy | **Open** | no ARM build carrying this codec exists to calibrate against |

---

## The documents

| | |
|---|---|
| [01 Overview](docs/01-overview.md) | what the two cartridges are, and the headline |
| [02 The two editions](docs/02-the-two-editions.md) | the internal control, and the seventeen differences |
| [03 Cartridge and file system](docs/03-cartridge-and-file-system.md) | header, layout, 5,145 files, classification by magic |
| [04 The executables](docs/04-executables.md) | `BLZ`, the step that mattered, the decompressor that was wrong, the secure area |
| [05 Who made it](docs/05-who-made-it.md) | the developer is named nowhere; `TO7` → `TO8` → `TO9`; the dates |
| [06 The block codec](docs/06-the-codec.md) | the constants, the structural probe, every `4080`, the blind decode |
| [07 What it compresses with instead](docs/07-compression.md) | 5,280 BIOS streams and zero BIOS calls |
| [08 The containers](docs/08-containers-and-assets.md) | `FPS4` little-endian, the field mask, the index/payload split, `V154` |
| [09 Budget and media](docs/09-budget-and-media.md) | every byte, 13 m 33 s of film, 6 h 38 m of sound |
| [10 Leftovers](docs/10-leftovers.md) | the debug archive, the build note, `STAN`, and four tools that were wrong |
| [11 Cross-title](docs/11-cross-title.md) | inwards, into the corpus, and outwards |
| [99 Open questions](docs/99-open-questions.md) | twelve, each with its measurement |

## The tools

[`tools/README.md`](tools/README.md) lists all of them and says which were
written here, which were fixed here and which came from a sibling pipeline
unchanged.

## Reproducing

```
python tools/ndsmodules.py IMAGE.nds --out modules/
python tools/ring_sites.py  modules/ --arm --dir --imm 4070,4071,4078,4079,4080
python tools/struct_probe.py --selftest
python tools/struct_probe.py modules/ --dir
python tools/bios_calls.py  modules/arm9.bin --base 0x02000000 --also modules/arm7.bin@0x02380000 [--also modules/ovl9_NNN.bin@0x0213A4E0 ...]
python tools/census.py      IMAGE.nds modules/ --control PHANTASIA.sfc
python tools/formats.py     IMAGE.nds modules/ --budget
python tools/media_census.py IMAGE.nds modules/
python tools/crosstitle.py  IMAGE.nds modules/ --other-rom IMAGE2.nds modules2/
```

## Licence

Tools MIT ([`LICENSE`](LICENSE)). Documentation and reports CC BY 4.0
([`LICENSE-DOCS`](LICENSE-DOCS)).
