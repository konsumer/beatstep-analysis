This is my attempt to reverse-engineer the firmware for Arturia Beatstep, and run my own firmware on it.

It's a stm32f103 (ARM) chip, so eventually I should be able to run ArduinoIDE, micropython, or similar on it. My goal is to figure out how to write code that can run on it, send sysex to it (so I don't need to wire up a JTAG interface) and map all of it's GPIO to to it's peripherals (buttons and LEDs.) My eventual goal is to write my own sequencer for it, for a standalone device.

While not directly applicable, [this](https://dsgruss.com/notes/2020/10/02/keystep1.html) has a great procedure for rev-engineering the firmware.


## Procedure

Download firmware from [here](https://www.arturia.com/support/downloads-manuals):

```
wget https://dl.arturia.net/products/beatstep/firmware/BeatStep_Firmware_Update_1_2_0_3.led
```

Extract the .led hex-file to binary:

```
./deled.py BeatStep_Firmware_Update_1_2_0_3.led  BeatStep_Firmware_Update_1_2_0_3.led.bin
```

Look at memory as image:

./imgmem.py BeatStep_Firmware_Update_1_2_0_3.led mem.png


Analyze in Ghidra, Arm Cortex, Little-endian:

![arm-cortex-le](https://dsgruss.com/assets/img/keystep/5-language-selection.png)
