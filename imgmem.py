#!/usr/bin/env python3

import sys
from PIL import Image

file_in=sys.argv[1]
file_out=sys.argv[2]

i=0
with open(file_in, "r") as f:
    line = f.readlines()[0]
    chunk = bytes.fromhex(line)
    im = Image.frombytes("L", (64, len(chunk) // 64), chunk)
    # I think it's always 1 line, but this is just in case
    if (i > 0):
        im.save(str(i) + "_" + file_out)
    else:
        im.save(file_out)
    i = i+1
