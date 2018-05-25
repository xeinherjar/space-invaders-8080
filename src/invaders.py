import cpu
import mem

class Motherboard:
    def __init__(self):
        self.cpu = cpu.CPU(self)
        self.ram = mem.MEM(self)


motherboard = Motherboard()

motherboard.ram.load('../roms/invaders.rom')
motherboard.cpu.run()
