#!/usr/bin/python3
# SPDX-License-Identifier: MIT
#
# extract just the program memory as a binary
# from source hex using objdump
#

import shutil
import sys
import os
from tempfile import NamedTemporaryFile
import subprocess

SRCFILE = './program/hl950.hex'
DSTFILE = './program/hl950_program.bin'
MPLABLOG = 'MPLABXLog.xml'
OBJCOPY = 'objcopy'

if len(sys.argv) > 1:
    SRCFILE = sys.argv[1]
if len(sys.argv) > 2:
    DSTFILE = sys.argv[2]

tmpf = {}
try:
    # copy program section out of source hex into a temp file
    tmpf['phex'] = NamedTemporaryFile(suffix='.hex',
                                      prefix='t_',
                                      mode='w',
                                      dir='.',
                                      delete=False)
    with open(SRCFILE) as f:
        dosec = False
        for l in f:
            if l.startswith(':02000004'):  # extended linear address
                if l[9:13] in [
                        '1D00',
                        '1D01',
                        '1D02',
                        '1D03',
                        '1D04',
                        '1D05',
                        '1D06',
                        '1D07',
                ]:
                    dosec = True
                    tmpf['phex'].write(l)
                else:
                    dosec = False
            elif l.startswith(':00000001FF'):
                tmpf['phex'].write(l)
            elif dosec:
                tmpf['phex'].write(l)
    tmpf['phex'].close()
    tmpf['pbin'] = NamedTemporaryFile(suffix='.bin',
                                      prefix='t_',
                                      dir='.',
                                      delete=False)
    tmpf['pbin'].close()
    subprocess.run(
        (OBJCOPY, '-Iihex', '-Obinary', tmpf['phex'].name, tmpf['pbin'].name),
        check=True,
        capture_output=True)
    os.rename(tmpf['pbin'].name, DSTFILE)

except Exception as e:
    print('Error:', e.__class__.__name__, e)
finally:
    for t in tmpf:
        if os.path.exists(tmpf[t].name):
            os.unlink(tmpf[t].name)
            print('Remove temp file:', t)
    if os.path.exists(MPLABLOG):
        os.unlink(MPLABLOG)
sys.exit(0)
