#!/usr/bin/env python3

import sys

file_in=sys.argv[1]
file_out=sys.argv[2]

with open(file_in, "r") as f:
    with open(file_out, "wb") as out:
        line = f.readlines()[0]
        chunk = bytes.fromhex(line)
        print("{} bytes found".format(len(chunk)))
        out.write(chunk)
