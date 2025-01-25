import logging
import struct

from dataclasses import dataclass
from PIL import Image


@dataclass
class Header:
    p1: bytearray
    offset: int
    p2: bytearray
    record_length: int

    def pack(self) -> bytearray:
        return struct.pack(">7sH7sH", self.p1, self.offset, self.p2, self.record_length)

    @classmethod
    def unpack(cls, data: bytearray):
        return cls(*struct.unpack(">7sH7sH", data))


@dataclass
class Footer:
    p1: bytearray
    checksum: int

    def pack(self) -> bytearray:
        return struct.pack("<" + str(len(self.p1)) + "sH", self.p1, self.checksum)

    @classmethod
    def unpack(cls, data: bytearray):
        return cls(*struct.unpack("<" + str(len(data) - 2) + "sH", data))


@dataclass
class Segment:
    header: Header
    data: bytearray
    footer: Footer

    def checksum(self) -> int:
        """Calculate the checksum for an individual segment"""
        checksum = sum(self.header.pack()[2:])
        checksum += sum(self.data)
        checksum += sum(self.footer.p1)
        return 0x10000 - (checksum & 0xFFFF)

    def recalculate(self):
        """Recalculate the checksum and store it"""
        self.footer.checksum = self.checksum()


class Firmware:
    def __init__(self, filename: str):
        """Read the firmware from the file and convert to binary"""

        self.data = bytearray()
        self.MEM_START = 0x0800000

        with open(filename, "r") as f:
            for line in f.readlines():
                chunk = bytes.fromhex(line)
                self.data.extend(chunk)
                logging.info("{} bytes found".format(len(chunk)))

    def save_full(self, filename: str):
        """Save all of the binary data (including headers) to a file"""

        with open(filename, "wb") as out:
            out.write(self.data)

    def save_full_bitmap(self, filename: str):
        """Pack all of the raw bytes into a bitmap"""

        im = Image.frombytes("L", (64, len(self.data) // 64), bytes(self.data))
        im.save(filename)

    def parse(self):
        """Parse and remove the headers and footers from the raw binary data"""

        self.segments = []

        i = 0
        while i < len(self.data):
            raw_header = self.data[i : i + 18]
            header = Header.unpack(raw_header)
            i += 18

            log = "seg {:3d} - {:X} \t {} : ".format(
                len(self.segments),
                self.MEM_START + (header.offset << 8),
                bytearray.hex(raw_header, " ", 1),
            )

            # A Special header is used to mean filling the entire record with FF

            if header.p1[:4] == bytes.fromhex("00 10 68 74"):
                self.segments.append(
                    Segment(header, bytearray.fromhex("FF" * 2048), None)
                )
                logging.info(log + "end")
                continue

            data = bytearray(self.data[i : i + header.record_length])
            i += len(data)

            # Last footer works a bit differently

            if len(self.data[i:]) >= 6:
              if self.data[i + 6] == 0xD:
                  raw_footer = self.data[i:]
                  footer = Footer.unpack(raw_footer)
                  i += 24
              else:
                  raw_footer = self.data[i : i + 12]
                  footer = Footer.unpack(raw_footer)
                  i += 12

            self.segments.append(Segment(header, data, footer))
            checksum = self.segments[-1].checksum()

            log += "({}) : {} \t {:02X} {:02X}".format(
                len(data),
                bytearray.hex(raw_footer[-10:], " ", 1),
                checksum % 256,
                checksum // 256,
            )
            logging.info(log)

    def save_payload(self, filename: str):
        """Write the raw data to a file without headers and footers"""

        with open(filename, "wb") as out:
            for s in self.segments:
                out.write(s.data)

    def checksum(self) -> int:
        """Calculate the total checksum for all the payloads"""

        outdata = bytes(b"".join(s.data for s in self.segments))
        total = 0x10000 - sum(outdata[:-2]) & 0xFFFF
        logging.info("Total checksum: {:02X} {:02X}".format(total % 256, total // 256))
        return total

    def save_payload_bitmap(self, filename: str):
        """Output data to bitmap without headers"""

        outdata = bytes(b"".join(s.data for s in self.segments))
        im = Image.frombytes("L", (64, len(outdata) // 64), outdata)
        im.save(filename)

    def patch_instruction(self, addr: int, a: int, b: int):
        """Patches an instruction at address from initial value a to b"""

        mem_offset = 0x08004000

        header_index = (addr - mem_offset) // 2048
        s = self.segments[header_index]
        patch_index = addr & 0x3FF
        log = bytearray.hex(s.data[patch_index - 4 : patch_index + 4], " ", 1)
        log += "\t\t->\t\t"

        assert s.data[patch_index] == a
        s.data[patch_index] = b
        s.recalculate()
        log += bytearray.hex(s.data[patch_index - 4 : patch_index + 4], " ", 1)

        checksum = s.checksum()
        logging.info(
            log + "\t\t{:02X} {:02X}".format(s.checksum() % 256, s.checksum() // 256)
        )

    def recalculate(self):
        """Recalculate the checksum for the final frame"""

        self.segments[-1].data[-2] = self.checksum() % 256
        self.segments[-1].data[-1] = self.checksum() // 256
        checksum = self.segments[-1].checksum()
        logging.info(
            "Final frame checksum: {:02X} {:02X}".format(
                checksum % 256, checksum // 256
            )
        )
        self.segments[-1].footer.checksum = checksum

    def save_led(self, filename: str):
        """Write the frames to a file back in the original format"""

        with open(filename, "w") as out:
            for s in self.segments:
                out.write(bytes.hex(s.header.pack()).upper())
                if s.footer:
                    out.write(bytearray.hex(s.data).upper())
                    out.write(bytes.hex(s.footer.pack()).upper())


if __name__ == "__main__":
    fname = "Keystep_Firmware_Update_1_0_1_15.led"
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    f = Firmware(fname)
    f.save_full(fname + ".bin")
    f.save_full_bitmap(fname + ".bin.bmp")
    f.parse()
    f.save_payload(fname + ".strip.bin")
    f.save_payload_bitmap(fname + ".strip.bin.bmp")
    f.checksum()
    print()
    patch_addresses = [
        (0x08017A0C, 6, 0),
        (0x08017A22, 4, 0),
        (0x08017A38, 2, 0),
        (0x08017A4E, 1, 0),
        (0x0801798E, 1, 0),
        (0x080179A4, 2, 0),
        (0x080179BA, 4, 0),
        (0x080179D0, 6, 0),
    ]
    for addr, a, b in patch_addresses:
        f.patch_instruction(addr, a, b)
    f.checksum()
    f.recalculate()
    f.save_led(fname + ".patched.led")
