#http://www.classiccmp.org/dunfield/r/8080.txt
#http://pastraiser.com/cpu/i8080/i8080_opcodes.html
class CPU:
    def __init__(self, bus):
        self.bus = bus
        self.pc = 0
        self.sp = 0
        self.cycles = 0
        self.registers = {
            'A': 0, # a:flags - program status word
            'B': 0, # b:c
            'C': 0,
            'D': 0, # d:e
            'E': 0,
            'H': 0, # h:l [address]
            'L': 0,
        }
        self.flags = {
            'S': False, # sign
            'Z': False, # zero
            # - 0
            'H': False, # AC auxillary carry
            # - 0
            'P': False, # parity
            # - 1
            'C': False, # condition
        }



    def nop(self):
        self.cycles += 4

    def

    function_map = [
        nop
    ]

    def step(self):
        # fetch, decode, execute
        op = self.bus['ram'].read(self.pc)
        self.pc += 1
        self.function_map[op](self)

    def run(self):
        while True:
            self.step()
