from cpu import *
from cli import *

cpu = CPU()
cli = CLI()

while True:
    inp = input('> ').lower().split(' ')
    if len(inp) == 0:
        continue

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
        exit()
    # Input was a CPU instruction
    else:
        info = cli.step(inp)
        cpu.step(info)
        cli.print_state(cpu)

    cli.buffer_push(cmd)
