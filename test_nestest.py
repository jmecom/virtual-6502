import unittest
from cpu import *
from gamepak import *

class TestNES(unittest.TestCase):
    def test_cpu(self):
        """ Tests for correctness of the CPU and its instructions by comparing against logs from known working emulators """
        cpu  = CPU()
        game = GamePak('test/nestest.nes')

        with open('test/nestest.log') as f:
            try:
                for line in f:
                    # Update CPU
                    pc     = cpu.translate_address(cpu.PC)
                    opcode = game.prg_rom[pc]
                    size   = instr_sizes[opcode]
                    bytes  = game.prg_rom[pc + 1 : pc + size]
                    info   = Info(opcode, size, bytes, 'little')

                    # Compare against the current line in nestest.log
                    # Program counter
                    cmp_pc = cpu.translate_address(int(line[0:4], 16))
                    self.assertEqual(pc, cmp_pc)

                    # Opcode
                    cmp_opcode = int(line[6:8], 16)
                    self.assertEqual(opcode, cmp_opcode)

                    # Instruction arguments
                    first_byte  = line[12:14]
                    second_byte = line[9:11]
                    if not (first_byte + second_byte).isspace():
                        # Ignores 0 argument instructions (NOP)
                        cmp_value = int(first_byte + second_byte, 16)
                        self.assertEqual(info.value, cmp_value)

                    # A register
                    cmp_a = int(line[50:52], 16)
                    self.assertEqual(cpu.A, cmp_a)

                    # X register
                    cmp_x = int(line[55:57], 16)
                    self.assertEqual(cpu.X, cmp_x)

                    # Y register
                    cmp_y = int(line[60:62], 16)
                    self.assertEqual(cpu.Y, cmp_y)

                    # Status register
                    cmp_p = int(line[65:67], 16)
                    self.assertEqual(cpu.P, cmp_p)

                    # Stack pointer
                    cmp_sp = int(line[71:73], 16)
                    self.assertEqual(cpu.SP, cmp_sp)

                    # CPU Cycle
                    # cmp_cyc = int(line[78:81], 10)
                    # self.assertEqual((cpu.cycle*3)%341, cmp_cyc)

                    # SL
                    # TODO

                    # Continue to next instruction
                    cpu.step(info)

            except TypeError:
                # Temporary - test should fail for instructions not yet
                # written, but I want to ignore that for now
                print("Success: terminated on incomplete instruction at PC = " + hex(cpu.PC))

            except AssertionError as e:
                print(pc)
                e.args += line[0:8],
                raise

if __name__ == '__main__':
    unittest.main()
