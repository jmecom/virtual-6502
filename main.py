import sys
from cpu import *
from cli import *

# TODO
# Write a parser for labels to run when program_name != None
# Finish the instruction set
# Allow for labels even in CLI mode
#
# Write and test some example progrmas
#
# Print 'status' in a nicer way
# Finish the README and help features
def main(program_name=None):
    cpu = CPU()
    cli = CLI(cpu)

    if program_name:
        cli.execute(program_name)
        sys.exit()
    else:
        print("Virtual6502 v1.1 \n"
        "Type help or view the readme for instructions. \n")

        while True:
            inp = input('> ').lower().split(' ')
            if len(inp) == 0:
                continue

            try:
                cmd = inp[0]
                if cmd in cli.cli_funcs:
                    # Input does not affect CPU
                    cli.cli_funcs[cmd](inp)
                else:
                    # Input was a CPU instruction
                    cpu.step(cli.step(inp))
                    cli.print_state(inp)
            except SystemExit:
                raise
            except:
                pass

            cli.buffer_push(cmd)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        main()
