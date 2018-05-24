import cpu
import mem

motherboard = { }
motherboard['cpu'] = cpu.CPU(motherboard)
motherboard['ram'] = mem.MEM(motherboard)

motherboard['ram'].load('../roms/invaders.rom')

motherboard['cpu'].run()
