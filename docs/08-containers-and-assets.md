# The containers

Two of them, both the studio's own, and the first is the one this repository
exists to name.

## `FPS4`, little-endian

The container on these cartridges is **`FPS4`** — the same container as the
Xbox 360 *Tales of Vesperia*, mastered five months earlier, where it is
big-endian.

```
+0x00  4  "FPS4"
+0x04  4  entry count, including a terminating entry
+0x08  4  offset of the entry table -- 0x1C on every archive in both corpora
+0x0C  4  offset of the first payload
+0x10  2  entry size
+0x12  2  field mask -- which per-entry fields exist, in bit order
+0x14  4  unknown
+0x18  4  offset of a trailing build-path string, 0 here
```

Every field is in the same place and means the same thing on both machines.
What differs is the byte order, and the reader decides it from the archive
rather than from a constant: the entry size at `+0x10` is a `u16` that reads
`0x2C` or `0x04` one way round and `0x2C00` or `0x0400` the other, so one
reading is plausible and the other is not; the table offset at `+0x08` agrees.
[`tools/fps4.py`](../tools/fps4.py).

**The byte order is the machine's and the structure is the line's**, which is
the shape of the finding this corpus already records for the nine-byte block
header — except in the opposite direction: there a little-endian header
survived onto a big-endian machine, here a big-endian container becomes
little-endian on a little-endian one.

| | Anime | CG |
|---|---:|---:|
| files whose first four bytes are `FPS4` | 56 | 56 |
| `FPS4` occurrences in the whole image | 2,493 | 2,493 |
| archives the reader descends into | **2,492** | **2,492** |
| archives it cannot read | 1 | 1 |

2,492 + 1 = 2,493. The magic sweep over the raw image and the container descent
agree exactly, which is the check that the descent is complete rather than
merely deep.

## The field mask, and a new way to misread it

*Tales of Vesperia* records the field mask as a silent-failure trap: an archive
states which of four per-entry fields exist, two masks occur on one disc, and a
reader that assumes the first reads the second's *name* as its *size* and
reports members of 1.4 GB inside a 10 KB file without raising an error.

Three masks occur here, and the third fails the other way round:

| Mask | Entry size | Fields | Where |
|---|---:|---|---|
| `0x000F` | 0x2C | offset, padded size, exact size, 32-byte name | most archives |
| `0x0003` | 0x08 | offset, padded size | the icon indexes |
| **`0x0001`** | **0x04** | **offset only** | **the archives nested inside those** |

A mask with no size field in it does **not** mean the sizes are missing. On
`0x0001` each member runs from its own offset to the next entry's, and the last
entry is a terminator whose offset is the archive's length — the same
convention the `0x000F` archives use for their final entry. A reader that
requires an explicit size finds no members at all and reports the archive as
unreadable.

That is what happened here first: **1,904 nested archives were reported
unreadable** before the reader learned the implicit form. The *Vesperia* trap
read a missing field as a present one; this one reads a present field as
missing. Both are silent, and the second is the more dangerous of the two on a
census, because it fails towards *fewer payloads* and a clean-looking zero.

## The index and the payload are two different files

Seventeen archives at the file-system level are an **index** whose entry
offsets point into a **separate payload file** beside it:

```
/m/m.b        67,008 bytes    1,521 entries, no payload of its own
/m/m.dat      65,918,912 bytes
```

Read alone, `m.b` is a file whose 1,521 members all run off its end — which is
an error, not a member list — and `m.dat` is a 65 MB opaque blob. Paired, they
are 1,521 members. The seventeen pairs are `char`, `cut_in`, `debug`, `Tex`,
`mag`, `map`, `fc`, `fcscr`, `ItemIcon`, `m`, `o`, `p`, `rmp`, `MENU_BG`,
`NAVIMAP_BG`, `EnemyIcon`, `SpirLinkIcon`.

**And the same split recurs inside.** `m.b` yields a member `AMUI00.B` which is
itself an `FPS4` whose offsets are into its sibling member `AMUI00.MAPBIN`. The
reader does not assume that from the naming: it tries each sibling sharing the
stem in turn and keeps the first for which **every** entry lands inside the
candidate, so the pairing is verified by the archive. **405 archives** are
paired that way, against 422 paired with a `.dat`.

The whole descent, from [`tools/census.py`](../tools/census.py):

```
Nintendo DS ROM
  -> BLZ-packed module        32 of 33 modules
  -> Nitro file system        5,114 named files, 31 overlays
    -> FPS4                   2,492 archives
      -> FPS4                 nested, and index/payload pairs both kinds
      -> V154                 1,508 objects
    -> BIOS stream            5,280
    -> nine-byte block        0
```

47,195 payloads and 376,083,362 bytes, against 5,145 files and 268,435,456
bytes at the top level.

## The one archive that cannot be read

`/m/misc/etc/tn.dat`, 188,416 bytes. Its first four bytes are `FPS4` and its
entry table does not resolve against itself or against any sibling. It is named
and counted rather than skipped, which is the property the corpus asks for; it
is 0.07% of the cartridge and it was swept as one opaque payload, so it is
covered by the blind decode even though it is not descended into.

## `V154`

The second container, 19 files and 1,508 objects once the descent reaches
them. It is the payload format behind the project's own `.ds3` extension.

```
+0x00  4  "V154"
+0x04  4  a small flag word -- 0x20, 0xE0, 0x120, 0x200
+0x08  4  0x6C on every object -- the header size
+0x14  4  length A
+0x18  4  length B      A + B == the object's total length
+0x24 ..  pairs of (count, offset) naming sub-tables
```

The length check is what makes the walk safe: `A + B` equals the object's own
size exactly on every standalone `.ds3` file, and the reader refuses the walk
when it does not, rather than producing regions that run off the end. The
`(count, offset)` pairs are used to split the body into regions so that each
gets its own plausibility bound in the census — which is the whole reason a
container has to be descended at all.

## What the containers hold

The commonest payload extensions across all 47,195 payloads:

| Extension | Payloads | What |
|---|---:|---|
| `.b` | 5,953 | a nested index |
| `.cmb` | 5,323 | map/model data |
| `.bin` | 3,827 | mixed |
| **`.ds3`** | **1,472** | the project's own, `V154` inside |
| `.scp` | 817 | script |
| `.dat` | 778 | mixed |
| `.nsbmd` / `.nsbca` / `.nsbma` / `.nsbta` / `.nsbtx` | 1,721 | NitroSDK models, animations and textures |
| `.lvd` | 518 | one per voice line |
| `.mapbin` / `.mapstat` | 810 | map payload and its status record |
| `.fcbin` | 376 | the `/fc` archive's members |
| **`.to9moh`** | **101** | the project tag, as an extension |

The NitroSDK model formats are used unchanged — this build did not write its own
model container, only its own archive.
