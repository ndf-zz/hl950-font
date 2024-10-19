# hl950-font

This respository contains an updated font for
mde 5 of the Tag Heuer HL950 Modulo display
based on
[Quicksand Medium](https://fonts.google.com/specimen/Quicksand).

## Usage

Scripts to read the firmware, remap the digits, patch the 
firmware and write it back to the device are provided in the
[scripts](scripts/) folder.

For displays with firmware version 1.1.07, use make:

	$ make clean
	$ make devwrite

Otherwise, extract the firmware to program/hl950.hex, and
check the offsets in fontpatch.py carefully:

	$ make devread

	FONTOFT = 0x9984
	LOGOOFT = 0x30018

## Font Map

   - [func_32x15.xcf](font/func_32x15.xcf) GIMP
   - [func_32x15.pbm](font/func_32x15.pbm) 3040x48 P4 PBM

Mode 5 on the display is a 2 column by one row layout
per module. The original units include a display font that
can be difficult to read and that does not present well
from a distance. This font uses a different size for numeric
digits and characters in order to maximise visibility
a long-distance:

![Digits](example_pbm_digits.png "Digits")

Each glyph is packed into 15 columns of 4 bytes,
with the LSB toward top of display, 
bytes ordered top to bottom. The first byte indicates
xadvance and is always 16 in this case:

![Packed Digits](example_map_digits.png "Packed Digits")

