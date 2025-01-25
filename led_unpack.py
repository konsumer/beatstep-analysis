#!/usr/bin/env python3

import sys
import os
from ledtobin import Firmware

try:
  filename_led = sys.argv[1]
except IndexError:
  print('Usage: led_unpack <LED_FILE>')
  exit(1)

b = os.path.splitext(os.path.basename(filename_led))[0]
filename_dump =  b + '.bin'
filename_stripped = b + '.strip.bin'
filename_image = b + '.png'
filename_image_stripped = b + '.png'

f = Firmware(filename_led)
f.save_full(filename_dump)
f.save_full_bitmap(filename_image)
f.parse()
f.save_payload(filename_stripped)
f.save_payload_bitmap(filename_image_stripped)
f.checksum()
