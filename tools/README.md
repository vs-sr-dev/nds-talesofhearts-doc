# Tools

Python 3 standard library only. No dependencies. Every report under
[`../reports/`](../reports) is one of these tools' output, prefixed with the
edition it was run on.

Run with `PYTHONIOENCODING=utf-8` on Windows — several of these print
Shift-JIS and UTF-16 text.

## Written for this cartridge

| Tool | What it does |
|---|---|
| `ndsmodules.py` | **step zero.** Extracts the ARM9, the ARM7 and all 31 overlays and decompresses `BLZ`, reporting the packed state from three independent sources — the overlay table's flag, the module parameters' `compressed_static_end`, and the footer — and checking each overlay's plaintext against the length the linker declared for it. 31 of 31 agree. |
| `sdkinfo.py` | the `[SDK+VENDOR:COMPONENT]` list, over the shipped image **and** over the plaintext modules, with the difference printed. |

## Rewritten for this platform

These keep their name and their job and their descent is new, because the
containers are.

| Tool | What changed |
|---|---|
| `census.py` | the blind decode census. The Xbox 360 descent (XDVDFS, big-endian `FPS4`, XCompress, ASF, RIFF) is replaced by the DS one: `BLZ` plaintext modules, the Nitro file system, little-endian `FPS4` including its index/payload split at two levels, `V154`, BIOS streams, and the nine-byte block. 47,195 payloads against 5,145 files. |
| `formats.py` | classification by magic and the `--budget` tessellation, over the Nitro file system and the same descent. The budget checks that its pieces sum to the image and prints the discrepancy. |
| `media_census.py` | Mobiclip `MODS` (including the 8.24 fixed-point frame-rate field), CRI ADX/AHX, and `SDAT` through its own `FAT` rather than by tag search. Names what it cannot parse instead of skipping it. |
| `deflate_control.py` | by class, over the Nitro file system, with the executable appearing twice — packed as shipped and in plaintext — because the difference between those two rows is the only measurement of what the linker's compressor achieved. |

## Fixed here

Each of these was wrong in a way that fails towards a clean-looking negative,
and each defect had survived because no previous target exercised it.

| Tool | Defect |
|---|---|
| `ndscomp.py` | the `BLZ` decompressor assembled a match token's two bytes in the wrong order, and did not clamp the copy to the end of the encoded region. It had never been executed: *Tempest* has no overlays and *Innocence*'s three are stored plain. 32 of 33 modules on these cartridges are packed. |
| `fps4.py` | a field mask with no size field in it was read as an archive with no members, rather than as one whose members run to the next entry's offset. 1,904 nested archives were reported unreadable. Also made byte-order-aware, deciding from the archive rather than from a constant. |
| `datestamps.py` | the `__DATE__` pattern required two spaces between month and day — right for `Jan  1 2008`, wrong for `Nov 19 2008`, which is the only compiler date on either cartridge. Also given `--modules`, because 32 of 33 modules are packed and the shipped image shows two fragments of one string where the plaintext shows nine stamps. |
| `leftovers.py` | given a `--who` mode searching ASCII, Shift-JIS **and** UTF-16LE, and a token-boundary test for class names — without one, a regular expression over compressed payload invents 3,240 identifiers on this cartridge and all of them are inside high-entropy buffers. |

## Extended here

| Tool | What was added |
|---|---|
| `ring_sites.py` | `--dir`, which runs the ARM scan over every module in a directory and prints one row each plus a totals row. A DS build is 33 modules and 71% of the ARM immediates are in the overlays, so a single-image count covers under a third of the code. |
| `struct_probe.py` | `--dir` with the same argument, and `--selftest`, which hand-assembles every fingerprint in every form the file looks for and checks the detector fires. It exists because **no ARM build carrying this codec is known**, so the probe's zero has no same-toolchain positive behind it, and that has to be visible above the number rather than after it. |
| `nearmiss.py` | a second form of the trigonometric-table test. On *Tempest* the 4,096-scaled cosine table was compiled into 446 constant-returning stubs; here it is a plain array, and the stub test scored zero on it. |
| `crosstitle.py` | `--other-rom IMAGE MODULEDIR`, which runs the identical descent over a second cartridge so the two sides are payload lists rather than file lists. That is what makes the two-edition control a payload-level measurement. |
| `magic_sweep.py` | this cartridge's needles, and a chance-rate table that puts 256 MiB beside 128 MB, 4.29 GB and 7.84 GB — because the same count carries opposite weight on the four. |

## Carried unchanged

`ndsrom.py`, `bios_calls.py`, `lzprobe.py`, `disarm.py`, `securearea.py`,
`sdat.py`, `symbols.py` from
[nds-talesofinnocence-doc](https://github.com/vs-sr-dev/nds-talesofinnocence-doc);
`internal_names.py`, `prefix_scan.py`, `common_run.py`, `aska.py`, `rtti.py`
from
[xbox360-talesofvesperia-doc](https://github.com/vs-sr-dev/xbox360-talesofvesperia-doc).

*Tales of Innocence*'s `ezbind.py` is **not** carried, because there is nothing
here for it to read: the `EZBIND` magic returns **0** on both cartridges against
a chance rate of under 0.001, and the container on these is `FPS4`.

`prefix_scan.py` and `common_run.py` are carried and **not run**. The strong
byte test needs a needle from a known decoder, there is no ARM decoder for this
codec anywhere in the corpus, and running either with a PowerPC or MIPS needle
would measure how much two instruction encodings share.

## The reference decoder

`tales_block.py` is the corpus's own, copied and **not** rewritten:

```
md5  e2dcd6b8dc717b84f67bf8a46568298c
```

It is committed here even though it found nothing, and its control — the 1995
Super Famicom cartridge, which must return **1,089** blocks — is run in the
same invocation as the census on each cartridge and does.
