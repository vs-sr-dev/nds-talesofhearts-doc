#!/usr/bin/env python3
"""How much video and audio is on the cartridge, measured from the headers.

Every duration here is read out of a header the file writes about itself:
frame counts, sample counts and sample rates.  Nothing is inferred from a file
name, an extension or a directory, and nothing is estimated from a byte count.

Three formats, and the cartridge names two of them and not the third:

  * **`MODS`** -- Actimagine Mobiclip, which the ARM9's SDK component list
    calls `[SDK+Actimagine:Mobiclip SDK V1.0.2]`.  Its header states the frame
    count, the frame size, the audio sample rate and -- in 8.24 fixed point --
    the **frame rate**, so a duration needs nothing the file does not say.
  * **`SDAT`** -- the NitroSDK sound archive.  Its streamed music lives in
    `STRM` members and its samples in `SWAR` archives of `SWAV` records, and
    both state their own sample rate and length.  The members are reached
    through the archive's own `FAT`, not by searching for tags, because a tag
    search over 21 MB of ADPCM finds tags that are not records.
  * **CRI ADX and AHX** -- which the SDK component list does **not** name.
    Eight CRI components are linked into the ARM9 and stamped with their own
    build dates, and 8,912 copies of the string `(c)CRI` are on the cartridge,
    and not one `[SDK+CRI:...]` tag exists.  The component list is therefore
    not a complete statement of what a build licensed, which is worth knowing
    before quoting one.

**A tool that cannot parse something must say so rather than skip it.**  On
*Tales of Vesperia* a media census nearly lost 230 MB of music in silence
because a container used a chunk it did not know; the tool now names what it
could not read, and that property is kept here.

    python media_census.py IMAGE MODULEDIR
    python media_census.py IMAGE MODULEDIR --csv media.csv

Standard library only.
"""

import collections
import csv as csvmod
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census
import sdat as sdatlib


def hms(sec):
    sec = int(round(sec))
    return "%d h %02d m %02d s" % (sec // 3600, (sec % 3600) // 60, sec % 60)


def read_mods(buf):
    """Everything a Mobiclip header states about itself.

    The fields are read off the files rather than taken from a specification,
    and each is checked against something the cartridge already says:

      +0x08  u32  frame count
      +0x0C  u32  width           256 on every file -- the DS screen
      +0x10  u32  height          192 on every file
      +0x14  u32  **frame rate, 8.24 fixed point**
      +0x18  u32  audio: channels in the low half, zero when there is none
      +0x1C  u32  audio sample rate, zero when there is none
      +0x20  u32  the largest frame, in bytes
      +0x28  u32  an offset inside the file
      +0x30  u32  0x4548 on every file here

    The frame rate is the field that makes a duration possible and it is the
    one worth showing the working for.  Seven of the nine files carry
    0x17F9DB23 and two carry 0x0BFCED91, and

        0x17F9DB23 / 2**24 = 23.976   = 24000/1001, the NTSC film rate
        0x0BFCED91 / 2**24 = 11.988   = exactly half of it

    which is what a rate field looks like and what an arbitrary constant does
    not.  The two halves also agree with the rest of the header: the two
    slower files are the two halves of one cutscene, `MOV000_A` and
    `MOV000_B`, and `MOV000_B` is the only file on the cartridge with a zero
    in both audio fields.
    """
    if buf[:4] != b"MODS" or len(buf) < 0x38:
        return None
    tag = buf[4:8]
    (frames, width, height, rate_fx, audio, arate, maxframe, off24,
     off28, hdr, k30) = struct.unpack_from("<IIIIIIIIIII", buf, 8)
    if not (0 < frames < 1 << 20):
        return None
    if not (0 < width <= 256 and 0 < height <= 192 * 2):
        return None
    fps = rate_fx / float(1 << 24)
    if not (1.0 <= fps <= 120.0):
        return None
    if arate and not (4000 <= arate <= 48000):
        return None
    return {
        "tag": tag, "frames": frames, "width": width, "height": height,
        "fps": fps, "rate_fx": rate_fx, "arate": arate,
        "chans": audio & 0xFFFF, "maxframe": maxframe, "hdr": hdr,
    }


def read_adx(buf):
    """Sample rate and total samples from a CRI ADX/AHX header."""
    if len(buf) < 0x20 or buf[0] != 0x80 or buf[1] != 0x00:
        return None
    copy_off = struct.unpack_from(">H", buf, 2)[0]
    enc = buf[4]
    chans = buf[7]
    rate, nsamples = struct.unpack_from(">II", buf, 8)
    if not (4000 <= rate <= 48000) or not (0 < chans <= 8):
        return None
    if not (0 < nsamples < 1 << 28):
        return None
    tail = buf[copy_off - 2:copy_off + 4] if copy_off + 4 < len(buf) else b""
    return {
        "enc": enc, "chans": chans, "rate": rate, "samples": nsamples,
        "cri": b"(c)CRI" in buf[:copy_off + 8],
        "kind": {0x02: "ADX", 0x03: "ADX", 0x10: "AHX", 0x11: "AHX"}.get(
            enc, "ADX-family 0x%02X" % enc),
    }


def read_sdat(buf):
    """Every member of a NitroSDK sound archive, through its own FAT.

    `STRM` is streamed music: its `HEAD` block states the sample rate at +0x1C
    and the number of samples at +0x24.  `SWAR` is a wave archive: its own
    table gives the offset of each `SWAV`, and each of those states its rate
    and its length.  Anything the reader does not recognise is returned in
    `unparsed` and printed, rather than dropped.
    """
    try:
        a = sdatlib.Sdat(buf)
        members = a.fat()
    except Exception:
        return None
    out = {"sections": {}, "strm": [], "swav": 0, "swav_samples": 0.0,
           "swav_rates": collections.Counter(), "unparsed": [],
           "counts": collections.Counter(), "bytes": 0}
    nblocks = struct.unpack_from("<H", buf, 0x0E)[0]
    for i in range(min(nblocks, 8)):
        boff, bsize = struct.unpack_from("<II", buf, 0x10 + i * 8)
        if 0 < boff < len(buf):
            tagname = buf[boff:boff + 4].decode("latin1", "replace")
            out["sections"][tagname] = (boff, bsize)
    for off, size in members:
        mem = buf[off:off + size]
        out["bytes"] += size
        tag = bytes(mem[:4])
        out["counts"][tag.decode("latin1", "replace")] += 1
        if tag == b"STRM" and size > 0x40:
            # STRM carries a `HEAD` block at +0x10: wave type at +0x18,
            # channel count at +0x1A, sample rate at +0x1C and the sample
            # count at +0x24.  Read from the block rather than guessed.
            rate = struct.unpack_from("<H", mem, 0x1C)[0]
            period = struct.unpack_from("<H", mem, 0x1E)[0]
            nsam = struct.unpack_from("<I", mem, 0x24)[0]
            # The rate field is identified by the field beside it rather than
            # asserted: on all 27 records here `period == 0x1000000 /
            # (rate * 32)` to within one, which is what a sample rate and its
            # timer reload look like together and what two arbitrary fields do
            # not.  Three rates occur -- 16,364, 22,767 and 52,365 Hz -- and
            # the ceiling below is 65,536 rather than 48,000 because a DS sound
            # channel is timer-driven and reaches that; 32,768 is the
            # recommended maximum, not the possible one.
            if 4000 <= rate <= 65536 and 0 < nsam < 1 << 27:
                out["strm"].append((rate, nsam))
            else:
                out["unparsed"].append(("STRM", off, size))
        elif tag == b"SWAR" and size > 0x3C:
            n = struct.unpack_from("<I", mem, 0x38)[0]
            if not 0 < n < 1 << 16:
                out["unparsed"].append(("SWAR", off, size))
                continue
            for i in range(n):
                o = struct.unpack_from("<I", mem, 0x3C + i * 4)[0]
                if not 0 < o < size - 0x10:
                    out["unparsed"].append(("SWAV", off + o, 0))
                    continue
                rate = struct.unpack_from("<H", mem, o + 2)[0]
                if not 4000 <= rate <= 48000:
                    out["unparsed"].append(("SWAV", off + o, 0))
                    continue
                # A SWAV record states its own length: the loop point and the
                # non-loop length are both counts of 32-bit words, so the data
                # is (loop + length) * 4 bytes, and how many samples that is
                # depends on the wave type in the record's first byte.
                wtype = mem[o]
                loop_w = struct.unpack_from("<H", mem, o + 6)[0]
                len_w = struct.unpack_from("<I", mem, o + 8)[0]
                nbytes = (loop_w + len_w) * 4
                if not 0 < nbytes <= size:
                    out["unparsed"].append(("SWAV", off + o, nbytes))
                    continue
                if wtype == 0:                      # 8-bit PCM
                    nsam = nbytes
                elif wtype == 1:                    # 16-bit PCM
                    nsam = nbytes // 2
                elif wtype == 2:                    # 4-bit IMA ADPCM
                    nsam = max(0, nbytes - 4) * 2
                else:
                    out["unparsed"].append(("SWAV", off + o, nbytes))
                    continue
                out["swav"] += 1
                out["swav_rates"][rate] += 1
                out["swav_samples"] += nsam / float(rate)
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    image, moddir = argv[1], argv[2]
    rows = []
    unparsed = []
    mods = []
    adx = collections.Counter()
    adx_secs = collections.Counter()
    adx_bytes = collections.Counter()
    adx_rates = collections.Counter()
    sdat = []
    n_payloads = 0
    for label, buf in census.Enumerator(image, moddir).payloads():
        n_payloads += 1
        if len(buf) < 16:
            continue
        b = bytes(buf)
        m = read_mods(b)
        if m:
            mods.append((label, len(b), m))
            continue
        a = read_adx(b)
        if a:
            adx[a["kind"]] += 1
            adx_secs[a["kind"]] += a["samples"] / float(a["rate"])
            adx_bytes[a["kind"]] += len(b)
            adx_rates[(a["kind"], a["rate"], a["chans"])] += 1
            continue
        if b[:4] == b"SDAT":
            s = read_sdat(b)
            if s:
                sdat.append((label, len(b), s))
            else:
                unparsed.append((label, len(b), "SDAT header not readable"))
            continue
        if b[:4] in (b"STRM", b"SWAR"):
            unparsed.append((label, len(b), "known audio tag, not parsed here"))

    print("payloads examined: %d" % n_payloads)
    print("")

    print("=== Actimagine Mobiclip video (`MODS`)")
    print("%-16s %10s %7s %9s %8s %6s %5s %10s"
          % ("file", "bytes", "frames", "size", "fps", "audio", "chan",
             "duration"))
    tot_f = 0
    tot_b = 0
    tot_s = 0.0
    for label, n, m in sorted(mods):
        secs = m["frames"] / m["fps"]
        print("%-16s %10d %7d %4dx%-4d %8.3f %6d %5d  %s"
              % (os.path.basename(label), n, m["frames"], m["width"],
                 m["height"], m["fps"], m["arate"], m["chans"], hms(secs)))
        tot_f += m["frames"]
        tot_b += n
        tot_s += secs
    if mods:
        print("%-16s %10d %7d %38s" % ("TOTAL", tot_b, tot_f, hms(tot_s)))
        print("")
        rates = sorted({m["rate_fx"] for _, _, m in mods})
        for r in rates:
            print("  rate field 0x%08X / 2**24 = %.4f frames per second"
                  % (r, r / float(1 << 24)))
        print("  24000/1001 = %.4f, and half of it = %.4f"
              % (24000 / 1001.0, 12000 / 1001.0))
        print("  version tag in every header: %r" % mods[0][2]["tag"])
    print("")

    print("=== CRI ADX / AHX")
    print("%-22s %8s %14s %s" % ("kind", "files", "bytes", "duration"))
    for k in sorted(adx):
        print("%-22s %8d %14d %s" % (k, adx[k], adx_bytes[k], hms(adx_secs[k])))
    print("%-22s %8d %14d %s"
          % ("TOTAL", sum(adx.values()), sum(adx_bytes.values()),
             hms(sum(adx_secs.values()))))
    print("")
    print("  rate and channel combinations actually used:")
    for (k, r, c), n in adx_rates.most_common():
        print("      %-6s %6d Hz  %d channel(s)  x%d" % (k, r, c, n))
    print("")

    print("=== NitroSDK sound archive (`SDAT`)")
    for label, n, sd in sdat:
        print("  %s, %d bytes" % (label, n))
        print("    blocks   : %s" % ", ".join(sorted(sd["sections"])))
        print("    members  : %s"
              % ", ".join("%s x%d" % (k, v)
                          for k, v in sorted(sd["counts"].items())))
        strm_secs = sum(ns / float(r) for r, ns in sd["strm"])
        print("    STRM     : %d members, %s of streamed music"
              % (len(sd["strm"]), hms(strm_secs)))
        for r, c in collections.Counter(r for r, _ in sd["strm"]).most_common():
            print("        %6d Hz  x%d" % (r, c))
        print("    SWAV     : %d records, %s at their own rates"
              % (sd["swav"], hms(sd["swav_samples"])))
        for r, c in sd["swav_rates"].most_common(6):
            print("        %6d Hz  x%d" % (r, c))
        print("    records this reader could not parse : %d"
              % len(sd["unparsed"]))
        for kind, off, size in sd["unparsed"][:10]:
            print("        %s at 0x%X, %d bytes" % (kind, off, size))
    print("")

    print("=== what this tool could not read")
    if not unparsed:
        print("  nothing: every payload with a media tag was parsed.")
    for label, n, why in unparsed[:40]:
        print("  %-40s %10d  %s" % (label, n, why))
    print("")

    if "--csv" in argv:
        path = argv[argv.index("--csv") + 1]
        with open(path, "w", newline="") as f:
            w = csvmod.writer(f)
            w.writerow(["kind", "label", "bytes", "seconds"])
            for label, n, m in mods:
                w.writerow(["mods", label, n,
                            m["samples"] / float(m["rate"]) if m["rate"] else 0])
            for k in adx:
                w.writerow([k, "", adx_bytes[k], adx_secs[k]])
        print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
