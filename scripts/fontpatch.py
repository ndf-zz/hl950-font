#!/usr/bin/python3
# SPDX-License-Identifier: MIT
#
# replace font and logo bitmaps in hl950 program code
#

from struct import pack

# constants
SRCBIN = './program/hl950_program.bin'
SRCFONT = './font/func_32x15.data'
SRCLOGO = './font/bootlogo.data'
SRCPROG = './program/hl950.hex'
DSTHEX = './program/alt_program.hex'
BASEADDR = 0x1d000000

FONTOFT = 0x9984
FONTLEN = 95 * 61
LOGOOFT = 0x30018
LOGOLEN = 4 * 32


def ihexline(address, record, buf):
    """Return intel hex encoded record for the provided buffer"""
    addr = pack('>H', address)
    sum = len(buf) + record
    for b in addr:
        sum += b
    for b in buf:
        sum += b
    sum = (~(sum & 0xff) + 1) & 0xff
    return ':%02X%s%02X%s%02X\n' % (len(buf), addr.hex().upper(), record,
                                    buf.hex().upper(), sum)


def dumpihex(file, image, base):
    """Dump program image data to intel hex"""
    plen = len(image)
    count = 0
    addr = base
    stride = 0x10
    grouplen = 0x10000 // stride
    for j in range(0, 8):
        # emit extended linear address
        ela = pack('>H', addr >> 16)
        file.write(ihexline(0, 0x04, ela))
        for i in range(0, grouplen):
            linelen = min(stride, plen - count)
            la = addr & 0xffff
            buf = pack('%dB' % (linelen), *image[count:count + linelen])
            file.write(ihexline(la, 0, buf))
            count += linelen
            addr += linelen


# load original program into mem - 512KB
PROGMEM = bytearray()
with open(SRCBIN, 'rb') as f:
    for j in range(0, 512):
        PROGMEM.extend(f.read(1024))
print('Read', len(PROGMEM), 'bytes from', SRCBIN)

# load modified fontmap - 5795B
FONTMAP = None
with open(SRCFONT, 'rb') as f:
    FONTMAP = f.read(FONTLEN)
print('Read', len(FONTMAP), 'bytes from', SRCFONT)

# load modified logo - 128B
LOGOMAP = None
with open(SRCLOGO, 'rb') as f:
    LOGOMAP = f.read(LOGOLEN)
print('Read', len(LOGOMAP), 'bytes from', SRCLOGO)

# write modified fontmap into program image
for j in range(0, FONTLEN):
    doft = FONTOFT + j
    PROGMEM[doft] = FONTMAP[j]

# write modified bootlogo to program image
for j in range(0, LOGOLEN):
    doft = LOGOOFT + j
    PROGMEM[doft] = LOGOMAP[j]

# write out modified program image
with open(DSTHEX, 'w') as f:
    dumpihex(f, PROGMEM, BASEADDR)
    dosec = False
    with open(SRCPROG) as g:
        for l in g:
            if l.startswith(':02000004'):  # extended linear address
                if l[9:13] in ['1FC0']:
                    dosec = True
                    f.write(l)
                else:
                    dosec = False
            elif dosec and not l.startswith(':00000001FF'):
                f.write(l)
    f.write(ihexline(0, 1, b''))

print('Wrote updated program image to:', DSTHEX)
