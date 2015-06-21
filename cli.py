import sys, readline
from cpu import *
from cpu_constants import *

class CLI():
    """Provides a command line interface for 6502 CPU"""

    def __init__(self):
        self.cmd_buffer = []

        self.cli_funcs = {
            'state': self.print_state, 'status': self.print_status,
            'history': self.print_history, 'mem': self.print_memory,
            'exit': self.exit
        }

        self.cmds = ['state', 'status', 'history', 'mem', 'exit'] + \
        [i.lower() for i in instr_names]

        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

    def completer(self, text, state):
        """Defines the completer used for readline's autocomplete"""
        options = [c for c in self.cmds if c.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None

    def execute(self, cpu, filename):
        """Exectues a program from a file"""
        with open(filename) as f:
            for line in f:
                inp = line.rstrip().split(' ')
                cmd = inp[0]

                if cmd in self.cli_funcs:
                    self.cli_funcs[cmd](cpu, inp)
                else:
                    cpu.step(self.step(inp))
                    self.print_state(cpu, inp)

    def step(self, inp):
        """Takes in a instruction from the user and returns an Info object
        to be passed to the CPU"""
        try:
            instr  = inp[0].upper()
            opcode = instr_names.index(instr)
            arg    = bytes.fromhex(inp[1])
            return Info(int(opcode), instr_sizes[opcode], arg, 'big')
        except IndexError:
            print("Error: missing arguments to command")
            raise
        except:
            print('Error: invalid command')
            raise

    def buffer_push(self, cmd):
        """Appends a command to the command history buffer"""
        self.cmd_buffer.append(cmd)

    def print_state(self, cpu, inp):
        """Prints the current state of the CPU"""
        print("A:%s X:%s Y:%s P:%s SP:%s CYC:%d" % (format(cpu.A, 'x'), \
        format(cpu.X, 'x'), format(cpu.Y, 'x'), format(cpu.P, 'x'), \
        format(cpu.SP, 'x'), (cpu.cycle*3)%341))

    def print_status(self, cpu, inp):
        """Prints the status register"""
        # TODO print this in a better way
        print("%s" % format(cpu.P, 'b'))

    def print_history(self, cpu, inp):
        """Prints the command input history"""
        for cmd in self.cmd_buffer:
            print(cmd)

    def print_memory(self, cpu, inp):
        """Prints a segment of memory"""
        try:
            print(cpu.memory[int(inp[1])])
        except:
            print('Error: memory location out of range')
            raise

    def exit(self, cpu, inp):
        sys.exit()
