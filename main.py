import sys
from cpu import *
from cli import *

def main():
    cpu = CPU()
    cli = CLI()

    while True:
        inp = input('> ').lower().split(' ')
        if len(inp) == 0:
            continue

        try:
            # Input does not affect CPU
            cmd = inp[0]
            if cmd == 'exec':
                cli.execute(inp[1])
            elif cmd == 'state':
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
                info = cli.step(inp)
                cpu.step(info)
                cli.print_state(cpu)
        except SystemExit:
            raise
        except:
            pass

        cli.buffer_push(cmd)

if __name__ == '__main__':
    main()
