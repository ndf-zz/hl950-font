#!/usr/bin/python3
# SPDX-License-Identifier: MIT
#
# Read fontmap from pbm and transpose glyph bits into packed
# hl950 bitmap format
#
# Each mode 5 glyph is packed into 15 columns of 4 bytes,
# LSB toward top of display, ordered top to bottom, with
# a single byte header indicating the glyph's xadvance.
#
# Refer to examples:
#
#  ./font/example_pbm_digits.png fontmap digits layout
#  ./font/example_map_digits.png packed bitmap digits layout
#
# Source fontmap bytes, PBM w=16 h=32
#
#    0   1
#    2   3
#    ...
#    62  63
#
# Memory data h=32 w=15
#
#    hdr
#    0   1   2   3
#    4   5   6   7
#    ...
#    56  57  58  59

import sys
from math import ceil

SRCFILE = './font/func_32x15.pbm'
DSTFILE = './font/func_32x15.data'

if len(sys.argv) > 1:
    SRCFILE = sys.argv[1]
if len(sys.argv) > 2:
    DSTFILE = sys.argv[2]

# Load PBM font map data
srcdata = None
with open(SRCFILE, 'rb') as f:
    srcdata = f.read()
if not srcdata.startswith(b'P4\x0a'):
    print('Input not PBM')
    sys.exit(-1)
imgw = None
imgh = None
idx = 0

# Skip comments
while True:
    idx = srcdata.index(b'\x0a', idx + 1)
    if srcdata[idx + 1] != 0x23:  # not a comment '#'
        break

# Read dimensions
eol = srcdata.index(b'\x0a', idx + 1)
wt, ht = srcdata[idx:eol].decode('ascii', 'ignore').split()
width = int(wt)
height = int(ht)
idx = eol + 1
print('Read P4: %d x %d, data offset: 0x%02x' % (
    width,
    height,
    idx,
))

# Prepare output data buffer
digdat = bytearray(61 * 95)

# Transpose bits from src chars into packed bitmap font data
srcstride = int(ceil(width / 8))  # bytes
for ch in range(0, 95):
    doft = 61 * ch  # destination offset
    digdat[doft] = 0x0f  # char width on panel, fixed at 16px
    doft += 1
    srcwoft = (32 * ch + 8) // 8  # bytes
    srchoft = 8  # lines
    lb = [0, 0]
    for i in range(0, 32):
        soft = idx + (srchoft + i) * srcstride + srcwoft

        # First byte
        srcidx = soft
        srcpx = (~srcdata[srcidx]) & 0xff
        dbcnt = i // 8
        dblshift = i % 8
        dboft = doft + dbcnt
        for r in range(0, 8):
            dcoft = r * 4
            if srcpx & 0x80:
                digdat[dcoft + dboft] |= (1 << dblshift)
            srcpx <<= 1

        # Second byte
        srcidx += 1
        srcpx = (~srcdata[srcidx]) & 0xfe
        #dbcnt = i//8  # TODO: verify l/r shift in dest
        #dblshift = i%8
        #dboft = doft + dbcnt
        for r in range(8, 15):
            dcoft = r * 4
            if srcpx & 0x80:
                digdat[dcoft + dboft] |= (1 << dblshift)
            srcpx <<= 1

# Write out font map
with open(DSTFILE, 'wb') as f:
    f.write(digdat)
print('Wrote packed font bitmap data to:', DSTFILE)
