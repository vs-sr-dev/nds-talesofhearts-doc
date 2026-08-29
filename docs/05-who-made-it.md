# Who made it

This page exists because the answer decides how everything else here has to be
written. The corpus's open question since 2006 is whether the block codec's
boundary is the *Tales* codebase or something else, and the control it has been
asking for is a Nintendo DS title **from the studio line** rather than from a
studio outside it. Whether this cartridge is that control depends on who built
it.

**The cartridge does not say.** What it does say is a project number, and the
project number is the whole of the evidence.

## The developer is named nowhere

Searched in **ASCII, Shift-JIS and UTF-16LE**, over the shipped image and over
all 33 plaintext modules, 271,287,520 bytes
([`tools/leftovers.py --who`](../tools/leftovers.py),
[`reports/anime-whomade.txt`](../reports/anime-whomade.txt)):

| Needle | ASCII | Shift-JIS | UTF-16LE |
|---|---:|---:|---:|
| `テイルズスタジオ` / `tales studio` | 0 | **0** | **0** |
| `株式会社` | — | **0** | **0** |
| `ウルフチーム` / `wolfteam` | 0 | 0 | 0 |
| `アルファ・システム` / `alfa system` | 0 | 0 | 0 |
| `dimps` | 0 | — | — |
| `ganbarion`, `monolith`, `tri-ace`, `tri-crescendo` | 0 | — | — |
| `スタッフ` (staff) | — | **0** | 0 |

Not one company string on either cartridge, in any alphabet. There is no
credits text file, no `.comment`, no symbol table, and — because the build was
compiled with RTTI off — no class-name list either.

## The publisher is named, in exactly one place

| Needle | Where |
|---|---|
| `バンダイナムコゲームス` (UTF-16LE) | the **banner**, six times: once per language slot |
| `ナムコ`, `バンダイ`, `バンダイナムコ` (UTF-16LE) | the same six banner strings |
| `NAMCO` (ASCII) | six times, all inside `TITLE_LOGO_NAMCO.NCGR_lz` / `.NCLR_lz` / `.NSCR_lz` — in the file name table and in an archive's entry table |

That is the whole of it. The publisher is on the box; the developer is not on
the cartridge.

## What *is* there: a project number

Four prefixes occur in the file names, and one of them settles the lineage
question as far as it can be settled from bytes:

| Tag | Where | Count |
|---|---|---:|
| **`TO9` / `To9`** | `/btl/prm/To9_EncountAreaData.dat`, `To9_EncountGroupData.dat`, `To9_EncountTable.dat`, `To9_DialogueData.bin`, `To9_BattleEventData.bin`, `To9_EnemyData.dat`; **the file extension `.to9moh`** on 101 container members; and the string `TO9:%s` in a debug overlay's version banner | 6 file names, 107 internal names, 1 format string |
| `TODS3` | ten root data files, `/TODS3_BtlMemoData.dat` and the rest | 10 |
| `CTODS3` | four shop tables under `/item/` | 4 |
| `TODS9` | six data tables under `/item/`, and the paths for them in the ARM9 | 6 |

And **`.ds3`** is the extension of 16 files and 1,472 container members — the
project's own extension for its `V154` objects, and the same 3.

### Why `TO9` matters

The corpus already records two of these tags, read from two other repositories
rather than assumed here:

| Tag | Title | Year | Platform | Carries the codec? |
|---|---|---|---|---|
| **`TO7`** | *Tales of the Abyss* | 2005 | PlayStation 2 | **yes** — 47,513 of 47,513 blocks |
| **`TO8`** | *Tales of Vesperia* | 2008 | Xbox 360 | **yes** — 8,255 of 8,255 blocks |
| **`TO9`** | **this cartridge** | **2008** | **Nintendo DS** | **no** |

*Tales of the Abyss* leaves twenty-five absolute source paths under
`C:\TO7\prog\`; *Tales of Vesperia*'s executable is literally named
`TO_8_360.exe` and its scenario container opens `TO8SCEL`. Both are Namco Tales
Studio builds. This cartridge is the next number in that scheme, five months
after `TO8`.

**This is Consistent, not Verified**, and the distinction is the point. What is
verified is that the string `TO9` is in these bytes in those four roles. What
is *read from elsewhere* is that `TO7` and `TO8` belong to two line builds. A
numbering scheme is not a signature, and nothing on this cartridge says who
holds the number.

### `TODS3` and `TODS9` on one cartridge

Both prefixes are on the same image, on different data tables, and neither
appears in the other's directory: `TODS3_*` in the root, `TODS9_*` and
`CTODS3_*` under `/item/`. The reading that fits both — the third *Tales* on
this machine (after *Tempest* 2006 and *Innocence* 2007) and the ninth project
of the line — is **Consistent**: it explains why two numbers coexist without
either being wrong, and nothing on the cartridge confirms either expansion.

## The SDK component list is not a complete statement

On a Nintendo DS the `[SDK+VENDOR:COMPONENT]` strings are usually the most
informative thing a cartridge volunteers about what it licensed. Here there are
**two** ([`tools/sdkinfo.py`](../tools/sdkinfo.py)):

```
[SDK+NINTENDO:BACKUP]
[SDK+Actimagine:Mobiclip SDK V1.0.2]
```

And here is what else is linked into the same ARM9, each naming and dating
itself ([`reports/anime-leftovers.txt`](../reports/anime-leftovers.txt)):

```
ADXT/NITRO      Ver.10.62  Build: Aug 26 2008 16:33:56
NITROCI/NITRO   Ver.1.04   Build: Aug 26 2008 16:33:58
ADXNITRO        Ver.1.07   Build: Aug 26 2008 16:33:59
NITRORNA/NITRO  Ver.1.06   Build: Aug 26 2008 16:34:00
MFCI/NITRO      Ver.1.23   Build: Aug 26 2008 16:34:00
AHX/NITRO       Ver.1.85   Build: Aug 26 2008 16:34:02
ADXCS/NITRO     Ver.1.25   Build: Aug 26 2008 16:34:02
CRI CRW:STD     Ver.0.83   Build: Aug 26 2008 16:34:03
```

Eight CRI components, `CRI-MW` as a string, the whole of CRI's error-message
table (`adxt_Create: parameter error` and forty more), a CRI file-system layer
whose functions are `nitroCiOpen` / `nitroCiReqRd`, and `(c)CRI` **8,912 times**
across the cartridge — two copies in each of the 4,456 voice files.

**And not one `[SDK+CRI:…]` tag.** *Tales of Innocence* licensed nine CRI
components and tagged them; this build licensed eight and tagged none. So the
component list says what a build *tagged*, which is not the same as what it
linked, and a census that quotes it as the licence list understates this
cartridge by eight.

## The dates

| | |
|---|---|
| CRI middleware, eight components | **26 August 2008**, 16:33:56 to 16:34:03 — one link, eight seconds wide |
| the game's own `__DATE__` | **19 November 2008**, in overlay 1, immediately beside `TO9:%s` and `heap %dK` in a debug version banner |
| release | 18 December 2008 |

Against the corpus's neighbours: *Tales of Vesperia*'s PE header is stamped
**2008-06-19** and its disc volume 2008-06-20; *Ratatosk no Kishi*'s last SDK
string is 2008-04-24 and its last asset timestamp 2008-05-19. So this build's
compiler stamp is **five months to the day** after *Vesperia*'s.

Finding it needed a repair. `datestamps.py` matched `__DATE__` with a pattern
requiring **two** spaces between month and day — correct for `Jan  1 2008`,
where the day is space-padded, and wrong for `Nov 19 2008`, where it is not.
The tool reported zero `__DATE__` stamps on a cartridge carrying one, which is
the only compiler date either cartridge has. [10](10-leftovers.md).

## What this page licenses the rest of the repository to say

**It licenses the platform-and-team question to be reported, and not to be
closed.** Everything measured here — the codec's absence, the container, the
compression, the budget — is a fact about a Namco Bandai *Tales* cartridge that
carries the project number after *Vesperia*'s. Whether the hands were the
line's is not answerable from these two images, and every page that leans on it
says so in the same sentence as the number.

The corpus's own precedent is *Tales of the Tempest*, which named its developer
nowhere and was written that way throughout. This is the second such build, and
the second time the answer is a property of the build settings — RTTI off, no
credits text, no symbol table — rather than of the studio.
