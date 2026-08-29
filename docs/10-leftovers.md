# Leftovers

What the build did not clean up. Categories that return nothing are printed as
zeros rather than left out, because on this corpus a silent category has twice
been the result.

## A debug directory shipped, on both cartridges

```
/btl/debug/debug.b     7,156 bytes   an FPS4 index, 161 members
/btl/debug/debug.dat  84,472 bytes   the payload
```

161 members named `DEBUG000.BIN` … , reached by the format string
`debug%03d.bin` in overlay 1. 91,628 bytes, 0.034% of the cartridge, byte
identical on both editions.

Overlay 1 also carries `Menu_Debug` and `Menu_Debug_Help` as strings, and the
version banner that gave up the build date:

```
heap %dK
TO9:%s
Nov 19 2008
```

`TO9:%s` and `Nov 19 2008` are four bytes apart. The project tag and the
compiler date are in the same debug string table, printed by the same overlay.

## `/movie/memo.txt`

Fifty bytes of Shift-JIS in the movie directory, on both cartridges, referenced
by no module:

```
Anime:  Info : 現在のデータはアニメーションムービーです
CG:     Info : 現在のデータはCGムービーです
```

A note to whoever was running the build, telling them which edition's assets
are in the tree. It shipped twice.

## `/menu/STAN.dat` — an eighth entry in a family of seven

This is the sharpest leftover on the cartridge and it needs its measurements
stated before its reading.

`/menu/` holds one 25,900-byte archive per playable character. Seven of them:

```
/menu/BERYL.dat     25,900      /menu/KOHAKU2.dat   25,900
/menu/HISUI.dat     25,900      /menu/KUNZITE.dat   25,900
/menu/INNES.dat     25,900      /menu/SHING.dat     25,900
/menu/KOHAKU.dat    25,900
```

and an eighth:

```
/menu/STAN.dat      25,900
```

Identical size, identical structure — one `.NCLR` palette and six 4,160-byte
`.NCBR` character-graphics banks, named `STAN.NCLR`, `STAN_1.NCBR` …
`STAN_6.NCBR`. There is no character called Stan in *Tales of Hearts*.

**It holds its own artwork, not a copy of another entry.** Against each of its
seven siblings it agrees on 27.2% to 34.9% of its bytes, which is what two
different 4-bit images in one layout give, and it deflates to 8,975 bytes,
inside the range the other seven occupy (9,428 to 12,891).

**And nothing in the executable names it.** Overlay 20 carries an explicit
table of the paths:

```
/menu/BERYL.dat  /menu/INNES.dat  /menu/HISUI.dat  /menu/SHING.dat
/menu/KOHAKU.dat  /menu/KOHAKU2.dat  /menu/KUNZITE.dat
/menu/Link_SHING.dat  /menu/Link_INNES.dat  /menu/Link_BERYL.dat
/menu/Link_HISUI.dat  /menu/Link_KOHAKU.dat  /menu/Link_KUNZITE.dat
/menu/Link_KOHAKU2.dat
```

Fourteen paths, seven characters, twice each. `STAN` is not among them, and the
string `STAN` — or `Stan`, or `stan` — occurs in **none of the 33 plaintext
modules**, on either cartridge. The seven siblings are each named twice; the
eighth is named nowhere.

There is also no `Link_STAN.dat`: whatever `STAN` was, it did not get the
second half of the treatment its siblings did.

**What it means is Open.** Three readings survive and nothing on the cartridge
chooses between them:

1. it is *Tales of Destiny*'s 1997 protagonist, スタン, left in the party-panel
   family as a placeholder or a cameo that was cut;
2. `STAN` is an abbreviation of something unrelated that happens to live in the
   same directory with the same layout;
3. it is an eighth entity that was cut for other reasons.

What can be said without choosing is in [11](11-cross-title.md), and it is the
part that matters to the corpus: **`dimlos` returns zero.** On *Tales of the
Tempest* the two names came as a pair — a character asset family named `stan`
and a sword-sized prop model named `dimlos` — and that pairing is what made the
placeholder reading fit. Here there is one and not the other.

## Source and path strings — and a false positive worth reading

**No absolute development path survives.** Scanned over all 33 plaintext
modules for a drive letter, `host0:`, `/home/` and `/usr/`: **zero**. No user
name, no workstation name, no build directory. *Tales of the Abyss* left
twenty-five `C:\TO7\prog\` paths and *Tales of the Tempest* left an artist's
desktop path inside an unconverted 3ds Max file; there is nothing of that kind
on either of these cartridges.

**And no source file name either**, which took one extra look to be sure of.
`leftovers.py` reports `Menu_Cursor.c` in the ARM9, and it is not a C file:
the bytes are

```
Menu_Cursor.pp  Menu_Cursor.cc  Menu_Cursor.ss
```

and the tool's pattern stopped at the first `.c`. `.cc`, `.pp` and `.ss` are
three of this project's own asset extensions — the container holds 137, 137 and
252 payloads with them — so the hit is an asset name truncated by a regular
expression, not a compiler leftover. Section 7's rule about reading every hit
applies to the innocent ones too.

What the modules do carry is the game's own file paths, 139 of them across the
33 modules, all of the form `/menu/MENU_BG.dat` or `/btl/prm/TO9_EnemyData.dat`
— runtime paths, not build paths.

## Diagnostics that shipped

A script virtual machine reports itself by name:

```
(CScript)Error : SetAccVar() VOID
(CScript)Error : Stack underflow.
(CScript)Error : Stack overflow.
```

Three messages, and the container holds 817 `.scp` payloads, so `CScript` is
the name of this build's script engine.

Two allocator tags — `SJRBF Error`, `SJMEM Error` — and the save-file name
template `NDSCARD%08x.%08x.%08x`.

The rest of the diagnostic text is CRI's, and there is a lot of it: the whole
`adxt_*` parameter-error table, `cvFsOpen #5:vtbl error` and its eleven
siblings, `CRISS is not initialized.`, and
`E2008011801: already ADXNITRO_SetupFs() called.` Those are the middleware's
strings, not the game's, and they are what
[05](05-who-made-it.md) uses to show the SDK component list is incomplete.

## English in a Japanese release

Every diagnostic above is English, and none of it is reachable from the game.
There is no English UI text, no second language table in the banner — all six
banner language slots hold the same Japanese string — and no English script.

## Names that say they are not content

| Pattern | Files | Bytes |
|---|---:|---:|
| `debug` | 2 | 91,628 |
| `test` / `dbg` / `dummy` / `sample` / `tmp` | 0 | 0 |
| leading underscore | 0 | 0 |

One category, and it is the debug archive above. The build is otherwise clean
of the naming the corpus usually finds — *Tales of Symphonia* shipped ten maps
named after members of its team, *Tales of the Tempest* shipped an artist's
desktop path. There is nothing of that kind here.

## Holes in the numbering

The movie set runs `MOV000_A`, `MOV000_B`, `MOV001` … `MOV007` with no gap. The
overlays run 0 to 30 with no gap. `/menu/` has `KOHAKU` and `KOHAKU2` and no
`SHING2`. The eight `sepia_*.ds3` files name the full cast — `beryl`,
`chalcedony`, `hisui`, `innes`, `kohaku`, `kunzite`, `lichia`, `shing` — while
`/menu/` covers only six of those eight plus `KOHAKU2` and `STAN`, so two of
the cast have no menu panel and one panel has no cast member.

## The tools that were wrong

Four defects were found by running tools against this cartridge that no
previous target had exercised. They are recorded here because each of them
fails in the direction of a clean-looking negative.

| Tool | Defect | What it would have cost |
|---|---|---|
| `ndscomp.py` (`BLZ`) | match-token bytes assembled in the wrong order | 32 of 33 modules unreadable — every count on [06](06-the-codec.md) drawn from packed bytes |
| `ndscomp.py` (`BLZ`) | the copy was not clamped to the end of the encoded region | the same, and silently corrupted output where it did not throw |
| `fps4.py` | a field mask with no size field read as having no members | 1,904 nested archives reported unreadable, and their contents never swept |
| `datestamps.py` | `__DATE__` pattern required two spaces between month and day | zero build dates reported on a cartridge carrying one — `Nov 19 2008` |

The first two are the important pair, and the reason they survived two DS
pipelines is that neither previous cartridge had a packed module to try them
on. The fix has a positive control that was on this cartridge the whole time:
the overlay table states each overlay's plaintext length, and **31 of 31
overlays decompress to exactly their declared length**. [04](04-executables.md).

`nearmiss.py` and `struct_probe.py` were also extended rather than fixed — the
first to recognise a trigonometric table stored as a plain array as well as one
compiled into stubs, the second to total its counts across a directory of
modules and to self-test its detectors. [99](99-open-questions.md) records what
each of those changes is worth.
