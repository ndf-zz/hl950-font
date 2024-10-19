#!/usr/bin/python3
# SPDX-License-Identifier: MIT
#
# Read bootlogo image and transpose bytes into hl950 format
#

import sys
from math import ceil

SRCFILE = './font/bootlogo.pbm'
DSTFILE = './font/bootlogo.data'

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
logodat = bytearray(4 * 32)

# Re-arrange bytes from src into memory format
for j in range(0, 32):
    oft = 4 * j
    logodat[oft] = ~srcdata[idx + oft + 3] & 0xff
    logodat[oft + 1] = ~srcdata[idx + oft + 2] & 0xff
    logodat[oft + 2] = ~srcdata[idx + oft + 1] & 0xff
    logodat[oft + 3] = ~srcdata[idx + oft] & 0xff

# Write out bootlogo data
with open(DSTFILE, 'wb') as f:
    f.write(logodat)
