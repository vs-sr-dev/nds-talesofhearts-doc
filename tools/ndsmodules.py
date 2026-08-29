#!/usr/bin/env python3
"""Step zero on a Nintendo DS: get the executable modules out, in plaintext.

Section 7 of the corpus makes this the first thing done on this platform and
gives the reason: `arm9.bin` and every overlay are normally packed with `BLZ`,
the Nintendo linker's backwards LZ, and a constant scan over a compressed
module returns zero and is indistinguishable from a clean negative.

Three independent statements about whether a module is compressed exist and
this tool prints all three rather than trusting one:

  * the **overlay table** carries a per-overlay `compressed` flag and a
    24-bit compressed length;
  * the ARM9's **module parameters** carry `compressed_static_end`, which is
    the RAM address the packed image ends at -- zero when nothing is packed;
  * the **`BLZ` footer** itself, eight bytes at the end of the module,
    which can be validated by decompressing and is not a claim anybody had
    to keep up to date.

  python ndsmodules.py IMAGE                 report every module
  python ndsmodules.py IMAGE --out DIR       write plaintext modules to DIR

Module parameters are located by their own magic pair, `nitro_code_be`
(0xDEC00621) followed by `nitro_code_le` (0x2106C0DE), which is how the
linker marks the struct; the struct begins 0x18 bytes in front of it.

Standard library only.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ndsrom import NDS
import ndscomp

MAGIC_PAIR = bytes.fromhex('2106C0DE') + bytes.fromhex('DEC00621')[::-1]
# nitro_code_be = 0xDEC00621 stored little-endian -> 21 06 C0 DE
# nitro_code_le = 0x2106C0DE stored little-endian -> DE C0 06 21
MAGIC_PAIR = b'\x21\x06\xC0\xDE\xDE\xC0\x06\x21'

SDK_KNOWN = {}


def module_params(arm9, ram_base):
    """Return the ModuleParams struct, or None. Located by its magic pair."""
    i = arm9.find(MAGIC_PAIR)
    if i < 0:
        return None
    off = i - 0x1C
    if off < 0:
        return None
    f = struct.unpack('<7I', arm9[off:off + 28])
    return {
        'file_off': off,
        'ram': ram_base + off,
        'autoload_list_start': f[0],
        'autoload_list_end': f[1],
        'autoload_start': f[2],
        'static_bss_start': f[3],
        'static_bss_end': f[4],
        'compressed_static_end': f[5],
        'sdk_version': f[6],
    }


def blz_status(data):
    """What the BLZ footer says, independently of anybody's flag."""
    if len(data) < 8:
        return (False, 'too short', None)
    enc_len, hdr_len, inc_len = struct.unpack('<I', data[-8:-4])[0], 0, 0
    hdr_len = (enc_len >> 24) & 0xFF
    enc_len &= 0xFFFFFF
    inc_len = struct.unpack('<I', data[-4:])[0]
    if inc_len == 0:
        return (False, 'length delta 0 (footer says: not packed)', None)
    if not (8 <= hdr_len <= 11) or enc_len == 0 or enc_len > len(data):
        return (False, 'footer implausible (enc=%d hdr=%d)' % (enc_len, hdr_len), None)
    try:
        out = ndscomp.blz_decompress(data)
    except Exception as e:
        return (False, 'footer plausible but decode failed: %s' % e, None)
    return (True, 'enc=%d hdr=%d delta=%d' % (enc_len, hdr_len, inc_len), out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    data = open(path, 'rb').read()
    r = NDS(data)
    out = None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
        os.makedirs(out, exist_ok=True)

    print('image                %s' % os.path.basename(path))
    print('')

    fat = r.fat()
    rows = []

    # ---- ARM9 -------------------------------------------------------------
    a9 = data[r.hdr['arm9_rom_off']:r.hdr['arm9_rom_off'] + r.hdr['arm9_size']]
    ram9_end = r.hdr['arm9_ram'] + r.hdr['arm9_size']
    mp = module_params(a9, r.hdr['arm9_ram'])
    if mp:
        print('module parameters at file +0x%X (ram 0x%08X)' % (mp['file_off'], mp['ram']))
        print('  autoload_list         0x%08X .. 0x%08X' % (mp['autoload_list_start'], mp['autoload_list_end']))
        print('  autoload_start        0x%08X' % mp['autoload_start'])
        print('  static_bss            0x%08X .. 0x%08X' % (mp['static_bss_start'], mp['static_bss_end']))
        print('  compressed_static_end 0x%08X   -> %s'
              % (mp['compressed_static_end'],
                 'ARM9 IS BLZ-packed' if mp['compressed_static_end'] else 'ARM9 is not packed'))
        cse = mp['compressed_static_end']
        print('  %-21s (arm9_ram + arm9_size = 0x%08X, %s)'
              % ('', ram9_end, 'agrees' if cse == ram9_end else 'DISAGREES'))
        print('  sdk_version           0x%08X' % mp['sdk_version'])
    else:
        print('module parameters    NOT FOUND (magic pair absent)')
    print('')

    ok, why, plain = blz_status(a9)
    rows.append(('arm9', len(a9), None, mp['compressed_static_end'] if mp else None, ok, why,
                 len(plain) if plain else len(a9)))
    if out:
        open(os.path.join(out, 'arm9.bin'), 'wb').write(plain if plain else a9)

    # ---- ARM7 -------------------------------------------------------------
    a7 = data[r.hdr['arm7_rom_off']:r.hdr['arm7_rom_off'] + r.hdr['arm7_size']]
    ok7, why7, plain7 = blz_status(a7)
    rows.append(('arm7', len(a7), None, None, ok7, why7, len(plain7) if plain7 else len(a7)))
    if out:
        open(os.path.join(out, 'arm7.bin'), 'wb').write(plain7 if plain7 else a7)

    # ---- overlays ---------------------------------------------------------
    for cpu in (9, 7):
        for o in r.overlays(cpu):
            s, e = fat[o['file_id']]
            raw = data[s:e]
            ok_o, why_o, plain_o = blz_status(raw)
            name = 'ovl%d_%03d' % (cpu, o['id'])
            rows.append((name, len(raw), o['compressed'], o['ram_size'], ok_o, why_o,
                         len(plain_o) if plain_o else len(raw)))
            if out:
                open(os.path.join(out, name + '.bin'), 'wb').write(plain_o if plain_o else raw)

    print('%-11s %10s %6s %10s %6s %10s %9s  %s'
          % ('module', 'rom bytes', 'flag', 'declared', 'blz', 'plaintext',
             'declared?', 'footer'))
    npacked = 0
    tot_rom = tot_plain = 0
    checked = agree = 0
    for name, n, flag, decl, ok, why, plainlen in rows:
        verdict = '-'
        if decl is not None:
            checked += 1
            verdict = 'OK' if decl == plainlen else 'MISMATCH'
            agree += 1 if decl == plainlen else 0
        print('%-11s %10d %6s %10s %6s %10d %9s  %s'
              % (name, n,
                 '-' if flag is None else ('yes' if flag else 'no'),
                 '-' if decl is None else str(decl),
                 'yes' if ok else 'no', plainlen, verdict, why))
        npacked += 1 if ok else 0
        tot_rom += n
        tot_plain += plainlen
    print('')
    print('%d of %d modules are BLZ-packed' % (npacked, len(rows)))
    print('%d bytes on the cartridge -> %d bytes of plaintext code' % (tot_rom, tot_plain))
    print('')
    print("The overlay table states each overlay's plaintext length in its own")
    print('`ram_size` field, which is written by the linker and not by this tool.')
    print('That is an independent check on the decompressor:')
    print('  %d of %d overlays decompress to exactly their declared length.' % (agree, checked))
    return 0


if __name__ == '__main__':
    sys.exit(main())
