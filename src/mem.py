# MEM MAP
# 0x0000 - 0x07FF - invaders.h
# 0x0800 - 0x0FFF - invaders.g
# 0x1000 - 0x17FF - invaders.f
# 0x1800 - 0x1FFF - invaders.e

# 0x2000 - 0x23FF - Work RAM
# 0x2400 - 0x3FFF - Video RAM

# 0x4000 - Mirror
class MEM:
    def __init__(self, bus):
        self.bus = bus
        self.ram = [0] * 0x4000
        self.mirror = 0x4000

    def write(self, idx, value):
        self.ram[idx % self.mirror] = value & 0xFF

    def read(self, idx):
        return self.ram[idx % self.mirror]

    def load(self, rom_path):
        with open(rom_path, 'rb') as f:
            rom = f.read()
            f.close()
        for idx, byte in enumerate(rom):
            self.ram[idx] = byte


