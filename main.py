import sys
from cpu import *
from cli import *

def main(program_name=None):
    cpu = CPU()
    cli = CLI()

    if program_name:
        cli.execute(cpu, program_name)

    else:
        while True:
            inp = input('> ').lower().split(' ')
            if len(inp) == 0:
                continue

            try:
                # Input does not affect CPU
                cmd = inp[0]
                if cmd == 'state':
                    cli.print_state(cpu)
                elif cmd == 'status':
                    cli.print_status(cpu)
                elif cmd == 'history':
                    cli.print_history()
                elif cmd == 'mem':
                    cli.print_memory(cpu, inp)
                elif cmd == 'exit':
                    sys.exit()
                # Input was a CPU instruction
                else:
                    cpu.step(info = cli.step(inp))
                    cli.print_state(cpu)
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
