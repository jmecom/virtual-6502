from cpu import *
from cpu_constants import *

class CLI():
    """ Provides a command line interface for 6502 CPU """

    def __init__(self):
        print('Virtual6502 v1.0')
        print('Type help or view the readme for instructions. \n')
        self.cmd_buffer = []

    def step(self, inp):
        """ Takes in a instruction from the user and returns an Info object
        to be passed to the CPU """
        try:
            instr  = inp[0].upper()
            opcode = instr_names.index(instr)
            arg    = bytes.fromhex(inp[1])
            return Info(int(opcode), instr_sizes[opcode], arg, 'big')
        except:
            raise
            print('Invalid use.')

    def buffer_push(self, cmd):
        self.cmd_buffer.append(cmd)

    def print_state(self, cpu):
        """ Prints the current state of the CPU """
        print("A:%s X:%s Y:%s P:%s SP:%s CYC:%d" % (format(cpu.A, 'x'), format(cpu.X, 'x'), format(cpu.Y, 'x'), format(cpu.P, 'x'), format(cpu.SP, 'x'), (cpu.cycle*3)%341))

    def print_status(self, cpu):
        print("%s" % format(cpu.P, 'b'))

    def print_history(self):
        for cmd in self.cmd_buffer:
            print(cmd)

    def print_memory(self, cpu, inp):
        """ Prints a segment of memory """
        try:
            idx = int(inp[1])
            print(cpu.memory[idx])
        except:
            raise
            print('Invalid use.')
