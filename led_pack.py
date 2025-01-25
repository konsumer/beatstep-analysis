#!/usr/bin/env python3

import sys
import os
from ledtobin import Firmware

try:
  filename_stripped = sys.argv[1]
except IndexError:
  print('Usage: led_unpack <BIN_FILE>')
  exit(1)

b = os.path.splitext(os.path.basename(filename_stripped))[0]
filename_led = b + '.led'

# TODO: rest of program
