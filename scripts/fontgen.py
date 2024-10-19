#!/usr/bin/python3
# SPDX-License-Identifier: MIT
#
# prepare initial 32x15 font bitmap document for hl950
# display mode 5 (1 row x 2 column) using Quicksand Medium
#
# Render digits at 31px, alpha and specials at 24px
#
# Quicksand font Copyright 2011 The Quicksand Project Authors
# licensed under the SIL Open Font License, Version 1.1.
# https://fonts.google.com/specimen/Quicksand/license
#
# Manual adjustments for LED display constraints contained in
# GIMP file font/func_32x15.xcf
#
# Notes:
#
#  - display appears to clip bottom two lines of bitmap
#  - chars are spaced so that there are two pizels of space
#    in the middle of a panel, to match the inter-panel spacing

import os
import sys
import cairo
from math import ceil

FONTMAPFILE = './font/func_32x15.png'
EXAMPLEFILE = './font/example.png'
EXAMPLEMSG = '1h53:47 +28:09.6'

GLYPH_W = 15
GLYPH_H = 32
GLYPH_BASELINE = GLYPH_H - 10
GLYPH_ALIGN = 8
GLYPH_FONT = 'Quicksand Medium'
GLYPH_FNH = 31
GLYPH_ALH = 24
GLYPH_SPECIALS = '!#$%&?@~+-{}[]|\/()'

CTR_W = 32
CTR_H = 48
CTR_WOFT = (CTR_W - GLYPH_W) // 2
CTR_HOFT = (CTR_H - GLYPH_H) // 2
CTR_BASELINE = CTR_WOFT + GLYPH_BASELINE
CTR_ALIGN = CTR_WOFT + GLYPH_W // 2
MAP_W = 32 * int(ceil((95 * CTR_W) / 32.0))

TP_W = 16 * 16
TP_H = 32


def glyph(cx, ch, w, h, clip=True):
    cx.save()
    cx.select_font_face(GLYPH_FONT, cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)
    letter = chr(ch + 0x20)
    if letter.isalpha() or letter in GLYPH_SPECIALS:
        cx.set_font_size(GLYPH_ALH)
    else:
        cx.set_font_size(GLYPH_FNH)

    fascent, fdescent, fheight, fxadvance, fyadvance = cx.font_extents()
    xbearing, ybearing, width, height, xadvance, yadvance = (
        cx.text_extents(letter))

    if clip:
        # clip glyph region
        xo = w + CTR_WOFT
        yo = h + CTR_HOFT
        cx.rectangle(xo, yo, GLYPH_W, GLYPH_H)
        cx.clip()
    else:
        if width > GLYPH_W:
            print('Warning: "%s" may exceed width %0.2f > %d' %
                  (letter, width, GLYPH_W))

    xo = w + CTR_WOFT
    yo = h + CTR_BASELINE + 0.5
    cx.move_to(xo - xbearing + (GLYPH_W - width) / 2, yo)
    cx.show_text(letter)
    cx.restore()


def box(cx, ch):
    cx.save()
    w = CTR_W * ch
    h = 0
    xo = w + CTR_WOFT - 0.5
    yo = h + CTR_HOFT - 0.5

    # borders
    cx.move_to(xo - 6, yo)
    cx.line_to(xo, yo)
    cx.line_to(xo, yo - 6)
    xo += GLYPH_W + 1
    cx.move_to(xo + 6, yo)
    cx.line_to(xo, yo)
    cx.line_to(xo, yo - 6)
    yo += GLYPH_H + 1
    cx.move_to(xo + 6, yo)
    cx.line_to(xo, yo)
    cx.line_to(xo, yo + 6)
    xo -= GLYPH_W + 1
    cx.move_to(xo - 6, yo)
    cx.line_to(xo, yo)
    cx.line_to(xo, yo + 6)

    # baseline
    yo = CTR_BASELINE + 0.5
    cx.move_to(xo - 8, yo)
    cx.line_to(xo - 4, yo)
    xo += GLYPH_W + 1
    cx.move_to(xo + 8, yo)
    cx.line_to(xo + 4, yo)

    cx.set_line_width(1.0)
    cx.stroke()
    cx.restore()


# Export the font reference bitmap
surface = cairo.ImageSurface(cairo.FORMAT_A1, MAP_W, CTR_H)
context = cairo.Context(surface)
for i in range(0, 95):
    box(context, i)
    w = CTR_W * i
    glyph(context, i, w, 0, clip=False)
surface.flush()
surface.write_to_png(FONTMAPFILE)
print('Initial font map saved to:', FONTMAPFILE)

# Example rendering

surface = cairo.ImageSurface(cairo.FORMAT_A1, TP_W, TP_H)
context = cairo.Context(surface)
msg = '1h53:47 +28:09.6'
w = -8
h = -8
for c in msg:
    glyph(context, ord(c) - 0x20, w, h)
    w += 16
surface.flush()
surface.write_to_png(EXAMPLEFILE)
