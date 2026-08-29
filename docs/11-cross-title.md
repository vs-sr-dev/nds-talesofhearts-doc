# Cross-title

Three directions, and the first of them is new to the corpus.

## 1. Inwards: the two editions

The internal control. Two cartridges, one day, one build:
**28,662 of 28,679 distinct payloads byte-identical**, all seventeen
differences located and every one of them the film or a structure that moves
because of it. [02](02-the-two-editions.md).

Every measurement below was run on both and is quoted from the Anime edition
because the two agree.

## 2. Outwards, inside the corpus

Both cartridges were compared against every neighbour the corpus has on the
same machine, and against the one five months earlier on a different machine
([`tools/crosstitle.py`](../tools/crosstitle.py),
[`reports/anime-crosstitle-corpus.txt`](../reports/anime-crosstitle-corpus.txt)).

| Against | Their payloads | Byte-identical | Shared names |
|---|---:|---:|---:|
| *Tales of Innocence*, DS 2007 | 6,378 files, 5,598 distinct | **1** | **0 of 29,778 against 4,959** |
| *Tales of the Tempest*, DS 2006 | 4,712 files, 3,855 distinct | **1** | **1 of 29,778 against 4,712** |
| *Tales of Vesperia*, Xbox 360 2008 | 162 files, 159 distinct | **0** | **0 of 29,778 against 162** |

The two "identical payloads" are read rather than counted, as they have to be:

* against *Innocence*, `field/kage.ntfp` — **two bytes**, both `0x00`;
* against *Tempest*, `data/default_font.mes` — **four bytes**, all `0xFF`.

Both are single-value runs matched against alignment slack on this side.
Neither is a shared asset, and the honest figure for all three comparisons is
**zero**.

The one shared name is `sound_data.sdat`, which is the NitroSDK's default name
for a sound archive and is on both DS cartridges for that reason.

**Total reconstruction, again.** This is the line's normal practice everywhere
the corpus has looked: *Tales of Vesperia* shares 0 of 11,154 payloads and 0 of
11,133 names with *Ratatosk no Kishi* six weeks earlier, and 0 and 1 with the
2003 GameCube disc.

## 3. The names, in both directions

56,324 distinct internal names were harvested through the containers
([`tools/internal_names.py`](../tools/internal_names.py)), and 29,778 distinct
member basenames through the archive directories. The cast of every other
title in the series:

| Needle | Names containing it |
|---|---:|
| `rutee`, `dimlos`, `cress`, `reid`, `veigue`, `senel`, `luke` | **0** each |
| `emil`, `marta`, `lloyd` | **0** each |
| `yuri`, `estelle`, `karol`, `rita`, `raven`, `judith`, `flynn`, `repede` | **0** each |
| **`stan`** | **7** — see below |

and this cartridge's own cast, which is the control on the search:

| Needle | Names containing it |
|---|---:|
| `shing` | 194 |
| `kohaku` | 159 |
| `hisui` | 131 |
| `beryl` | 129 |
| `innes` | 125 |
| `kunzite` | 105 |
| `lichia` | 1 |
| `chalcedony` | 0 |

So the instrument finds a cast where there is one, and finds none of the other
eight titles' casts anywhere. Two of the eight names in this game's own
`sepia_*.ds3` set — `chalcedony` at 0 and `lichia` at 1 — barely appear, so a
low count is a fact about how a given asset family is named and not about
whether the character is in the game. That cuts both ways and is the reason the
zeros above are quoted beside the six large positives rather than alone.

The *Vesperia* row deserves a note, because the corpus warns about it
explicitly: on that disc the cast lives in the asset names as **three-letter
codes** — `YUR`, `EST`, `KAR` — and searching for the full names returns zero
as a fact about the naming convention rather than about the assets. Both forms
were searched here. The three-letter forms return 38, 95 and 11 hits in a raw
byte sweep of the image against a chance rate of 16, and every one located is
inside high-entropy payload; in the *names*, where a hit is not a chance
survivor, they return zero.

### `stan`, and the pair that is not here

Seven names, and they are all one family: `STAN.NCLR`, `STAN_1.NCBR` …
`STAN_6.NCBR`, inside `/menu/STAN.dat` — an eighth entry in a seven-entry
family of party portraits, holding its own artwork, and named by no module.
[10](10-leftovers.md) has the measurements.

What matters to the corpus is the other half. *Tales of the Tempest* raised
`stan` and `dimlos` **as a pair**: a complete field-character asset family named
`stan` with `_field` and `_walk` animations, *and* a sword-sized prop model
named `dimlos`, which is the name of that character's sword in the 1997 game.
The pairing is what made the placeholder reading fit, and *Tales of Innocence*
withdrew it by returning zero `dimlos` and 23 `stan` hits that were all
`charastand` or `Standard`.

On this cartridge:

| | *Tempest* 2006 | *Innocence* 2007 | **Hearts 2008** |
|---|---|---|---|
| `stan` | a field-character family, `stan_0001`…`stan_0020` in a technique table, `"スタン"` as a speaker tag in four test scripts | 23 hits, all `charastand` / `Standard` | **7 hits, one menu-portrait family, unreferenced** |
| `dimlos` | one prop model, nine string occurrences | **0** | **0** |
| ディムロス | 0 | 0 | **0** |

Three DS cartridges, three different answers on `stan`, and `dimlos` on exactly
one of them. This is the third data point on that open question and the first
from a cartridge carrying the line's project number; it does not settle what
`STAN` means here, and it does narrow what the *Tempest* pair can be evidence
of, because the pairing does not recur.

## 4. The envelopes and the tags

A four-byte needle has a chance rate of **0.0625** on a 256 MiB medium, so a
single hit is worth locating and a zero is strong. That is the denominator
pointing the ordinary way round, and it is the first time in three sessions —
after a 4.29 GB Wii partition at 1.00 and a 7.84 GB Xbox 360 image at 1.82 —
that a count can be read at face value. ([`tools/magic_sweep.py`](../tools/magic_sweep.py),
[`reports/anime-magic-sweep.txt`](../reports/anime-magic-sweep.txt)).

| Needle | Hits | Expected | Read |
|---|---:|---:|---|
| **`FPS4`** | **2,493** | 0.0625 | the container — [08](08-containers-and-assets.md) |
| **`V154`** | **1,700** | 0.0625 | the second container |
| `(c)CRI` | **8,912** | <0.001 | two per voice file |
| `MODS` | 9 | 0.0625 | the nine movies |
| `SDAT` | 1 | 0.0625 | the sound archive |
| **`EZBIND`** | **0** | <0.001 | *Innocence*'s archive |
| **`NT_DS1`** | **0** | <0.001 | *Tempest*'s project tag |
| **`MSCF`** | **0** | 0.0625 | the 2003/Wii envelope |
| `top2`, `Top2`, `_custom`, `rutee`, `tod2_cut`, `HVQM4`, `.h4m` | 0 | | the 2003 GameCube disc |
| `THEIRSCE`, `FILE.FPB`, `TLPS`, `TLPK`, `FPS2`, `FPS3` | 0 | | the corpus's other containers |
| `ROFSBLD`, `SAMPLE_GAME_TITLE`, `CRID`, `@UTF`, `ADXF` | 0 | | CRI's other stamps |
| `VXDS` | 0 | 0.0625 | *Tempest*'s Actimagine `VX` |
| `CPS ` | 0 | 0.0625 | *Legendia*'s envelope |
| `CPS\0` | 4 | 0.0625 | all four inside high-entropy payload |
| `AFS\0`, `CVMH` | 1 each | 0.0625 | both inside high-entropy payload |
| `SCPK` | 2 | 0.0625 | both inside high-entropy payload |
| `tor_` | 4 | 0.0625 | all four inside the word `monitor_` |
| `TO7`, `TO8`, `ToR`, `ToL`, `tox` | 9, 7, 11, 6, 7 | **16** | at or below the noise floor; every one located is inside compressed payload |
| **`TO9`** | **116** | 16 | above it, and the located hits are file paths in the ARM9 |
| **`TODS3`** | **20** | <0.001 | file names |
| **`CTODS3`** | **6** | <0.001 | file names |

`tor_` is the sharp one and it repeats a lesson the corpus already learned the
hard way. On the Wii disc `tor_` returned 3,865 hits against a chance rate of
1.00 and every one was inside the word `vector_`; here it returns 4 and every
one is inside `monitor_`. The uniform model underestimates because names are
not uniform, and only reading them tells you which kind of hit you have.

## 5. Outwards, outside the corpus

**ASKA** — tri-Ace's engine, the baseline the corpus keeps checking for — was
run over both whole images and over all 33 plaintext modules of each
([`tools/aska.py`](../tools/aska.py),
[`reports/anime-aska.txt`](../reports/anime-aska.txt)). Nothing found: five
signatures return one to three hits over 0.25 GiB, none of them sound, and the
verdict is negative.

**And the negative is weak, for a reason that had to be measured first.** On
*Tales of Vesperia* the ASKA negative is strong because that build was compiled
with RTTI on and its 445 demangled class names contain no `Aska` namespace.
This build was compiled with RTTI **off** — five C++ names in 2,852,064 bytes
of plaintext, all of them the standard library's — so there is no class-name
list to check, and `docs/aska-across-titles.md` in the *Infinite Undiscovery*
pipeline is explicit that a miss on the magics alone proves very little. The
result is reported with that condition attached rather than as a clean zero.

**Middleware** present: Actimagine Mobiclip (tagged), CRI ADX/AHX/ADXT/MFCI and
a CRI file-system layer (eight components, none tagged), and the NitroSDK's own
`SDAT` and model formats. Not present: Bink, Miles, FMOD, Havok, CRI Sofdec 2,
CRI `ROFS`, CRI `AFS`, `CRID`, `@UTF` — all zero.

## What crossed, and what did not

| | |
|---|---|
| the block codec | **did not cross** to this cartridge |
| the `FPS4` container | **crossed**, from *Vesperia* five months earlier, structure intact and byte order changed to the machine's |
| the packer's `MSCF` envelope and its `5b 80 80 8d` preamble | **did not cross** — absent from both cartridges, as they were absent from *Vesperia* |
| any asset | **did not cross**, from any title, in either direction |
| any name | **did not cross**, from any title |
| the project numbering | **crossed** — `TO7`, `TO8`, `TO9` |

The corpus's shape after *Vesperia* was that the codec persists and the packer
varies. These two cartridges add a third thing that persists across a change of
machine, a change of byte order and five months: **the container's structure**.
`FPS4`'s header layout and its field-mask semantics are the same on a
PowerPC Xbox 360 disc and on an ARM Nintendo DS cartridge, with only the byte
order following the processor — which is the same behaviour the nine-byte block
header shows, in reverse.
