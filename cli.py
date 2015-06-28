import sys, readline
from cpu import *
from cpu_constants import *

class CLI():
    """Provides a command line interface for 6502 self.cpu"""

    def __init__(self, cpu):
        self.cpu = cpu
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

    def execute(self, filename):
        """Exectues a program from a file"""
        with open(filename) as f:
            for line in f:
                inp = line.rstrip().split(' ')
                cmd = inp[0]

                if cmd in self.cli_funcs:
                    self.cli_funcs[cmd](self.cpu, inp)
                else:
                    self.cpu.step(self.step(inp))
                    self.print_state(self.cpu, inp)

    def step(self, inp):
        """Takes in a instruction from the user and returns an Info object
        to be passed to the self.cpu"""
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

    def print_state(self, inp):
        """Prints the current state of the self.cpu"""
        print("A:%s X:%s Y:%s P:%s SP:%s CYC:%d" % (format(self.cpu.A, 'x'), \
        format(self.cpu.X, 'x'), format(self.cpu.Y, 'x'), format(self.cpu.P, 'x'), \
        format(self.cpu.SP, 'x'), (self.cpu.cycle*3)%341))

    def print_status(self, inp):
        """Prints the status register"""
        # TODO print this in a better way
        print("%s" % format(self.cpu.P, 'b'))

    def print_history(self, inp):
        """Prints the command input history"""
        for cmd in self.cmd_buffer:
            print(cmd)

    def print_memory(self, inp):
        """Prints a segment of memory"""
        try:
            print(self.cpu.memory[int(inp[1])])
        except:
            print('Error: memory location out of range')
            raise

    def exit(self, inp):
        sys.exit()
