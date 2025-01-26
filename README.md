This is my attempt to reverse-engineer the firmware for Arturia Beatstep, and run my own firmware on it.

It uses a [stm32f103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html) chip, with some supporting circuitry to multiplex all the buttons, leds, and knobs. It looks like they are using [hc574](https://www.ti.com/lit/ds/symlink/sn54hc574.pdf?ts=1587965539932) to multiplex rotoary-encoders. It looks like it has programming pins on board (`JP1`) but firmware updates over sysex would be preferrable. Eventually I should be able to run ArduinoIDE, micropython, or similar on it. My goal is to figure out how to write code that can run on it, send sysex to it (so I don't need to wire up a JTAG interface) and map all of it's GPIO to to it's peripherals (buttons and LEDs.) My eventual goal is to write my own sequencer for it, for a standalone device.

While not directly applicable, [this](https://dsgruss.com/notes/2020/10/02/keystep1.html) has a great procedure for rev-engineering the firmware.

I included a few small wrapper scripts:

- `led_unpack.py` - extract binary firmware and an image file so you can look at the structure
- `led_pack.py` - turn binary firmware into an .led file


## Reversing

This part isn't strictly needed, but can give some interesting insight into how it works.

Download firmware from [here](https://www.arturia.com/support/downloads-manuals):

```bash
wget https://dl.arturia.net/products/beatstep/firmware/BeatStep_Firmware_Update_1_2_0_3.led
```

Extract the .led hex-file to binary:

```bash
./led_unpack.py BeatStep_Firmware_Update_1_2_0_3.led
```

Now you can analyze the `.strip.bin` file in Ghidra, Arm Cortex, Little-endian:

![arm-cortex-le](https://dsgruss.com/assets/img/keystep/5-language-selection.png)


You can patch it, and send it back with `led_pack.py`:

```bash
./led_pack.py BeatStep_Firmware_Update_1_2_0_3.strip.bin
```
