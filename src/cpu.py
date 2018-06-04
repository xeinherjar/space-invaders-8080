#http://www.classiccmp.org/dunfield/r/8080.txt
#http://pastraiser.com/cpu/i8080/i8080_opcodes.html
from collections import namedtuple
from enum import IntFlag, Flag

class Registers:
    #AF A:Flags Program Status Word, HL [address]
    def __init__(self, cpu):
        self.cpu = cpu
        self.BC = 0 # idx 0
        self.DE = 0 # idx 1
        self.HL = 0 # idx 2
        self.SP = 0 # idx 3
        self.AF = 0

    def read_pair(self, idx):
        if idx == 0:
            return self.BC
        elif idx == 1:
            return self.DE
        elif idx == 2:
            return self.HL
        elif idx == 3:
            return self.SP
    
    def write_pair(self, idx, value):
        if idx == 0:
            self.BC = value
        elif idx == 1:
            self.DE = value
        elif idx == 2:
            self.HL = value
        elif idx == 3:
            self.SP = value

    def read_register(self, idx):
        # b:0, c:1, d:2, e:3, h:4, l:5, m:6, a:7
        # m = mem[ mem[hl] ]
        if idx == 0:
            return self.BC >> 8
        elif idx == 1:
            return self.BC & 0xF
        elif idx == 2:
            return self.DE >> 8
        elif idx == 3:
            return self.DE & 0xF
        elif idx == 4:
            return self.HL >> 8
        elif idx == 5:
            return self.HL & 0xF
        elif idx == 6:
            address = self.cpu.bus.ram.read(self.HL)
            return self.cpu.bus.ram.read(address)
        elif idx == 7:
            return self.AF >> 8
        else:
            raise ValueError('read_register: something is wrong', idx)

    def write_register(self, idx, value):
        # b:0, c:1, d:2, e:3, h:4, l:5, m:6, a:7
        # m = mem[ mem[hl] ]
        if idx == 0:
            low = self.BC & 0xF
            self.BC = (value << 8) | low
        elif idx == 1:
            high = self.BC >> 8
            self.BC = (high << 8) | value
        elif idx == 2:
            low = self.DE & 0xF
            self.DE = (value << 8) | low
        elif idx == 3:
            high = self.DE >> 8
            self.DE = (high << 8) | value
        elif idx == 4:
            low = self.HL & 0xF
            self.HL = (value << 8) | low
        elif idx == 5:
            high = self.HL >> 8
            self.HL = (high << 8) | value
        elif idx == 6:
            address = self.cpu.bus.ram.read(self.HL)
            self.cpu.bus.ram.write(address, value)
        elif idx == 7:
            low = self.AF & 0xF
            self.AF = (value << 8) | low
        else:
            raise ValueError('write_register: something is wrong', idx, value)


class Flags(IntFlag):
    S = 0b10000000 # sign
    Z = 0b01000000 # zero

    AC = 0b00010000 # auxillary carry

    P = 0b00000100 # parity
    IGNORE = 0b00000010
    C = 0b00000001 # carry


class CPU:
    CLEAR_FLAGS = 0b00000010

    def __init__(self, bus):
        self.bus = bus
        self.pc = 0
        self.cycles = 0
        self.registers = Registers(self)

    def get_flags(self):
        return Flags(self.registers.AF & 0xF)

    def set_flags(self, value, *args, left_value=None, right_value=None):
        """ *args flags to test and set for """
        flag = 0b00000010
        for arg in args:
            if arg == Flags.S and Flags.S in Flags(value):
                flag = flag | Flags.S
            elif arg == Flags.Z and value == 0:
                flag = flag | Flags.Z
            elif arg == Flags.AC:
                if (left_value & 0xf) + (right_value & 0xf) > 0xf
                    flag = flag | Flags.AC
            elif arg == Flags.P:
                mask = 0b10000000
                count = 0
                while mask != 0:
                    if value & mask:
                        count += 1
                    mask = mask >> 1
                if count % 2 == 0:
                    flag = flag | Flags.P
                
            elif arg == Flags.C and (value > 0xFF or value < 0x0):
                flag = flag | Flags.C
        acc = self.registers.AF >> 8
        self.registers.AF = (acc << 8) | flag


    def read_word(self):
        low = self.bus.ram.read(self.pc)
        high = self.bus.ram.read(self.pc + 1)
        self.pc += 2
        return (high << 8) | low

    def read_byte(self):
        value = self.bus.ram.read(self.pc)
        self.pc += 1
        return value
    
    def write_byte(self, address, value):
        self.bus.ram.write(address, value)

    # Instructions
    def AAA(self):
        raise ValueError('NOT IMPL 0x{:02x}'.format(self.op), self.op, "Cycles: ", self.cycles, "PC: 0x{:02x}".format(self.pc - 1), self.pc)

    def call(self):
        """ Unconditional subroutine call """
        address = self.read_word()
        high = self.pc >> 8
        low = self.pc & 0xF
        self.bus.ram.write(self.registers.SP - 1, high)
        self.bus.ram.write(self.registers.SP - 2, low)
        self.registers.SP += 2
        self.pc = address
        self.cycles += 17
    
    def dcr(self):
        # b:0, c:1, d:2, e:3, h:4, l:5, m:6, a:7
        # m = mem[ mem[hl] ]
        # flags affected, z,s,p,ac
        idx = (self.op & 0b00111000) >> 3
        if idx == 0:
            dec = (self.registers.BC >> 8) - 1
            low = self.registers.BC & 0xF
            self.registers.BC = ((dec & 0xF) << 8) | low
        elif idx == 1:
            high = self.registers.BC >> 8
            dec = (self.registers.BC & 0xF) - 1
            self.registers.BC = (high << 8) | (dec & 0xF)
        elif idx == 2:
            dec = (self.registers.DE >> 8) - 1
            low = self.registers.DE & 0xF
            self.registers.DE = ((dec & 0xF) << 8) | low
        elif idx == 3:
            high = self.registers.DE >> 8
            dec = (self.registers.DE & 0xF) - 1
            self.registers.DE = (high << 8) | (dec & 0xF)
        elif idx == 4:
            dec = (self.registers.HL >> 8) - 1
            low = self.registers.HL & 0xF
            self.registers.HL = ((dec & 0xF) << 8) | low
        elif idx == 5:
            high = self.registers.HL >> 8
            dec = (self.registers.HL & 0xF) - 1
            self.registers.HL = (high << 8) | (dec & 0xF)
        elif idx == 6:
            address = self.bus.ram.read(self.registers.HL)
            dec = self.bus.ram.read(address) - 1
            self.bus.write(address, dec)
            self.cycles += 5
        elif idx == 7:
            dec = (self.registers.AF >> 8) - 1
            low = self.registers.AF & 0xF
            self.registers.AF = ((dec & 0xF) << 8) | low
        else:
            raise ValueError('INR: something is wrong', idx)
        
        self.set_flags(dec, Flags.Z, Flags.S, Flags.P, Flags.AC, left_value=dec + 1, right_value=1)
        self.cycles += 5

    def inr(self):
        """ Increment register """
        # b:0, c:1, d:2, e:3, h:4, l:5, m:6, a:7
        # m = mem[ mem[hl] ]
        # flags affected, z,s,p,ac
        idx = (self.op & 0b00111000) >> 3
        if idx == 0:
            inc = (self.registers.BC >> 8) + 1
            low = self.registers.BC & 0xF
            self.registers.BC = ((inc & 0xF) << 8) | low
        elif idx == 1:
            high = self.registers.BC >> 8
            inc = (self.registers.BC & 0xF) + 1
            self.registers.BC = (high << 8) | (inc & 0xF)
        elif idx == 2:
            inc = (self.registers.DE >> 8) + 1
            low = self.registers.DE & 0xF
            self.registers.DE = ((inc & 0xF) << 8) | low
        elif idx == 3:
            high = self.registers.DE >> 8
            inc = (self.registers.DE & 0xF) + 1
            self.registers.DE = (high << 8) | (inc & 0xF)
        elif idx == 4:
            inc = (self.registers.HL >> 8) + 1
            low = self.registers.HL & 0xF
            self.registers.HL = ((inc & 0xF) << 8) | low
        elif idx == 5:
            high = self.registers.HL >> 8
            inc = (self.registers.HL & 0xF) + 1
            self.registers.HL = (high << 8) | (inc & 0xF)
        elif idx == 6:
            address = self.bus.ram.read(self.registers.HL)
            inc = self.bus.ram.read(address) + 1
            self.bus.write(address, inc)
            self.cycles += 5
        elif idx == 7:
            inc = (self.registers.AF >> 8) + 1
            low = self.registers.AF & 0xF
            self.registers.AF = ((inc & 0xF) << 8) | low
        else:
            raise ValueError('INR: something is wrong', idx)
        
        self.set_flags(inc, Flags.Z, Flags.S, Flags.P, Flags.AC, left_value=inc - 1, right_value=1)
        self.cycles += 5
    
    def inx(self):
        """ Increment register pair """
        idx = (self.op & 0b00110000) >> 4
        if idx == 0:
            self.registers.BC += 1
        elif idx == 1:
            self.registers.DE += 1
        elif idx == 2:
            self.registers.HL += 1
        elif idx == 3:
            self.registers.SP += 1
        self.cycles += 5

    def mov(self):
        """ Move register to register """
        source = self.op & 0b00000111
        destination = (self.op & 0b00111000) >> 3
        value = self.registers.read_register(source)
        self.registers.write_register(destination, value)
        self.cycles += 5
        if source == 6 or destination == 6:
            self.cycles += 2

    def nop(self):
        """ No operation """
        self.cycles += 4
    
    def ldax(self):
        """ Load indirect through BC or DE """
        idx = (self.op & 0b00110000) >> 4
        address = self.registers.read_pair(idx)
        flag = self.registers.AF & 0xF
        self.registers.AF = (address << 8) | flag
        self.cycles += 7

    
    def lxi(self):
        """ Load 16 bit Register from Immediate Value """
        value = self.read_word()
        idx = (self.op & 0b00110000) >> 4
        self.registers.write_pair(idx, value)
        self.cycles += 10

    def jmp(self):
        """ Unconditional jump """
        self.pc = self.read_word()
        self.cycles += 10
    
    def mvi(self):
        """ Move immediate to register """
        value = self.read_byte()
        idx = (self.op & 0b00111000) >> 3
        self.registers.write_register(idx, value)
        self.cycles += 7
    


    def step(self):
        # fetch, decode, execute
        self.op = self.bus.ram.read(self.pc)
        print('OP: 0x{:02x}'.format(self.op))
        self.pc += 1
        self.function_table[self.op](self)

    def run(self):
        while True:
            self.step()

    function_table = [
        #0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
        nop, lxi, AAA, AAA, AAA, dcr, mvi, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 0
        AAA, lxi, AAA, inx, AAA, AAA, AAA, AAA, AAA, AAA, ldax, AAA, AAA, AAA, AAA, AAA, # 1
        AAA, lxi, AAA, inx, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 2
        AAA, lxi, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 3
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 4
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 5
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 6
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, mov, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 7
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 8
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # 9
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # A
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # B
        AAA, AAA, AAA, jmp, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, call, AAA, AAA, # C
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # D
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, # E
        AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA, AAA  # F
    ]
