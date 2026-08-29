#!/usr/bin/env python3
"""What a Nintendo DS build says about itself: SDK components and versions.

The NitroSDK stamps a `[SDK+VENDOR:COMPONENT]` string into a module for every
licensed component linked into it, and the linker leaves the SDK's own version
in the module parameters.  On this platform that list is the most informative
thing a cartridge volunteers, because it names middleware that no other
structure on the cartridge has to mention.

It has to be run over the **plaintext** modules.  Every one of these strings on
*Tales of Hearts* lives inside a `BLZ`-packed module, so a scan of the shipped
image finds a fraction of them and reports the fraction as the list.  Both are
counted here and the difference is printed.

  python sdkinfo.py IMAGE MODULEDIR

Standard library only.
"""
import os
import re
import sys

TAG = re.compile(rb'\[SDK\+[\x20-\x7E]{1,80}?\]')
VER = re.compile(rb'(?:NitroSDK|NITRO-SDK|nitro-sdk)[\x20-\x7E]{0,60}')


def hits(buf):
    out = []
    for m in TAG.finditer(buf):
        out.append((m.start(), m.group().decode('ascii')))
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    image, moddir = sys.argv[1], sys.argv[2]
    raw = open(image, 'rb').read()

    print('# what the shipped image says, before anything is decompressed')
    inimage = hits(raw)
    for off, s in inimage:
        print('  image +0x%08X  %s' % (off, s))
    print('  %d component tags visible in the packed image' % len(inimage))
    print('')

    print('# what the plaintext modules say')
    seen = {}
    order = []
    for name in sorted(os.listdir(moddir)):
        if not name.endswith('.bin'):
            continue
        buf = open(os.path.join(moddir, name), 'rb').read()
        for off, s in hits(buf):
            print('  %-12s +0x%06X  %s' % (name, off, s))
            if s not in seen:
                seen[s] = []
                order.append(s)
            seen[s].append(name)
        for m in VER.finditer(buf):
            print('  %-12s +0x%06X  version string: %r'
                  % (name, m.start(), m.group().decode('ascii')))
    print('')
    print('# distinct components, %d' % len(order))
    for s in order:
        print('  %-46s in %s' % (s, ', '.join(sorted(set(seen[s])))))
    print('')
    print('%d tags in the packed image, %d occurrences over %d distinct components '
          'in the plaintext' % (len(inimage), sum(len(v) for v in seen.values()), len(order)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
