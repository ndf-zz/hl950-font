# SPDX-License-Identifier: MIT
#
# HL950 Replacement font
#

IPECMD = ./scripts/ipecmd
IPEOPTS = -TPPK4 -P32MX440F512H

.PHONY: fontpatch
fontpatch: ./program/alt_program.hex

./program/alt_program.hex: ./program/hl950_program.bin ./font/func_32x15.data ./font/bootlogo.data
	mkdir -p ./program
	./scripts/fontpatch.py

.PHONY: fontgen
fontgen: ./font/func_32x15.png

./font/func_32x15.png:
	./scripts/fontgen.py

.PHONY: fontconv
fontconv: ./font/func_32x15.data

./font/func_32x15.data: ./font/func_32x15.pbm
	./scripts/fontconv.py

.PHONY: logoconv
logoconv: ./font/bootlogo.data

./font/bootlogo.data: ./font/bootlogo.pbm
	./scripts/logoconv.py

.PHONY: devread
devread: ./program/hl950.hex

./program/hl950.hex:
	mkdir -p ./program
	$(IPECMD) $(IPEOPTS) -GFprogram/hl950.hex -OL

./program/hl950_program.bin: ./program/hl950.hex
	./scripts/extractprog.py ./program/hl950.hex ./program/hl950_program.bin

.PHONY: devwrite
devwrite: ./program/alt_program.hex
	$(IPECMD) $(IPEOPTS) -Fprogram/alt_program.hex -M -OL

.PHONY: clean
clean:
	-rm -f ./font/func_32x15.data ./font/bootlogo.data ./font/func_32x15.png ./program/* MPLABXLog.xml
	-rmdir --ignore-fail-on-non-empty ./program
