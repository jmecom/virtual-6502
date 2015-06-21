from bitutils import *
from cpu_constants import *

class Info():
    """ Contains information about an instruction """
    def __init__(self, opcode, size, bytes, endian):
        self.opcode = opcode
        self.size   = size
        self.bytes  = bytes
        self.value  = int.from_bytes(bytes, endian)

    def __str__(self):
        return str(str(opcode) + " " + format(self.address, '02x'))
        + " " + str(self.bytes)

class CPU():
    """ Emulates the NES 6502 CPU """
    def __init__(self):
        self.PC = 0xC000     # Program counter
        self.A  = 0x00       # Accumulator
        self.X  = 0x00       # X index
        self.Y  = 0x00       # Y index
        self.SP = 0xFD       # Stack pointer
        self.P  = 0b00100100 # Status register

        self.address_mode = IMMEDIATE # TODO
        self.memory = [0] * 65536
        self.cycle = 0
        self.SL = 241   # TODO implement this
        self.pc_set = False

    def step(self, info):
        """ Executes a single instruction """
        self.pc_set = False

        instr_functions[info.opcode](self, info)
        self.cycle += instr_cycles[info.opcode]
        if not self.pc_set:
            self.PC += info.size

    def translate_address(self, address):
        """ Translates a virtual address to 'physical' address in
        a .nes file """
        # 256 bytes per page
        # start at page C, so C000 -> 0000
        #            page offset (msb) + address (bottom 3 bytes)
        return -3072 + (address >> 12)*256 + (address & 4095)

    def print_state(self, info):
        """ Prints the current state of the CPU """
        bytes_str = " ".join([hex(b) for b in info.bytes])
        name = instr_names[info.opcode]

        status_str = "A:%s X:%s Y:%s P:%s SP:%s CYC:%d SL:%d" % \
        (format(self.A, 'x'), format(self.X, 'x'), format(self.Y, 'x'), \
        format(self.P, 'x'), format(self.SP, 'x'), (self.cycle*3)%341, self.SL)

        print(str(format(self.PC, '02x')) + " " + bytes_str +
         " "*(8-len(bytes_str)+2) + name + " "*4 + status_str)

    def set_pc(self, address):
        """ Sets the program counter to the specified address and prevents the
        PC from being incremented on the current step """
        self.PC = address
        self.pc_set = True

    def set_zero(self, value):
        """ Updates the status register's zero flag """
        if value == 0:
            self.P = set_bit(self.P, 1)
        else:
            self.P = clear_bit(self.P, 1)

    def set_neg(self, value):
        """ Updates the status register's neg flag """
        if value & 128 != 0:
            self.P = set_bit(self.P, 7)
        else:
            self.P = clear_bit(self.P, 7)

    def set_zero_neg(self, value):
        """ Updates the status register's neg and zero flags """
        self.set_neg(value)
        self.set_zero(value)

    def compare(self, reg, mem):
        """ Compares the value of a register with a value in memory, updating
        the zero, negative, and carry flags as appropriate """
        self.set_zero_neg(reg - mem)
        if reg >= mem:
            self.P = set_bit(self.P, 0)
        else:
            self.P = clear_bit(self.P, 0)

    def jmp(self, info):
        """ Sets the program counter to the specified address """
        self.set_pc(info.value)

    def ldx(self, info):
        """ Loads a byte of memory into the X register and updates the zero and
        negative flags as appropriate """
        self.X = info.value
        self.set_zero_neg(info.value)

    def stx(self, info):
        """ Stores the contents of the X register into memory """
        self.memory[info.value] = self.X

    def jsr(self, info):
        """ Pushes the address of the return point on to the stack and then
        sets the program counter to the target memory address """
        self.memory[self.SP] = self.PC + 3
        self.set_pc(info.value)
        self.SP -= 2

    def nop(self, info):
        """ Causes no changes to the processor other than the normal
        incrementing of the program counter to the next instruction """
        pass

    def sec(self, info):
        """ Sets the carry flag to one """
        self.P = set_bit(self.P, 0)

    def bcs(self, info):
        """ If the carry flag is set then add the relative displacement to
        the program counter to cause a branch to a new location """
        if self.P & 0b00000001:
            self.PC += info.value

    def clc(self, info):
        """ Sets the carry flag to zero """
        self.P = clear_bit(self.P, 0)

    def bcc(self, info):
        """ If the carry flag is clear then add the relative displacement
        to the program counter to cause a branch to a new location """
        if not self.P & 0b00000001:
            self.PC += info.value

    def lda(self, info):
        """ Loads a byte of memory into the accumulator setting the zero
        and negative flags as appropriate """
        self.A = info.value
        self.set_zero_neg(info.value)

    def beq(self, info):
        """ If the zero flag is set then add the relative displacement to
        the program counter to cause a branch to a new location """
        if check_bit(self.P, 1):
            self.PC += info.value

    def bne(self, info):
        """ If the zero flag is clear then add the relative displacement to
        the program counter to cause a branch to a new location """
        if not check_bit(self.P, 1):
            self.PC += info.value

    def sta(self, info):
        """ Stores the contents of the accumulator into memory """
        self.memory[info.value] = self.A

    def bit(self, info):
        """ This instruction is used to test if one or more bits are set in a
        target memory location. The mask pattern in A is ANDed with the value
        in memory to set or clear the zero flag, but the result is not kept.
        Bits 7 and 6 of the value from memory are copied into the N and
        V flags. """
        val = self.memory[info.value]
        self.P = copy_bit(val, self.P, 6) # Overflow
        self.P = copy_bit(val, self.P, 7) # Negative
        self.set_zero(self.A & val)

    def bvs(self, info):
        """ If the overflow flag is set then add the relative displacement to
        the program counter to cause a branch to a new location """
        if check_bit(self.P, 6):
            self.PC += info.value

    def bvc(self, info):
        """ If the overflow flag is clear then add the relative displacement to
        the program counter to cause a branch to a new location """
        if not check_bit(self.P, 6):
            self.PC += info.value

    def bpl(self, info):
        """ If the negative flag is clear then add the relative displacement to
        the program counter to cause a branch to a new location """
        if not check_bit(self.P, 7):
            self.PC += info.value

    def rts(self, info):
        """ The RTS instruction is used at the end of a subroutine to return to
        the calling routine. It pulls the program counter (minus one) from
        the stack """
        self.SP += 2
        self.set_pc(self.memory[self.SP])

    def sei(self, info):
        """ Set the interrupt disable flag to one """
        self.P = set_bit(self.P, 2)

    def sed(self, info):
        """ Set the decimal mode flag to one """
        self.P = set_bit(self.P, 3)

    def php(self, info):
        """ Pushes a copy of the status reg on to the stack with bit 4 true """
        self.SP -= 1
        self.memory[self.SP] = set_bit(self.P, 4)

    def pla(self, info):
        """ Pulls an 8 bit value from the stack and into the accumulator.
        The zero and negative flags are set as appropriate """
        self.A = self.memory[self.SP]
        self.SP += 1
        self.set_zero_neg(self.A)

    def and_(self, info):
        """ Performs a logical AND on the accumulator using the contents of a
        byte of memory, updating zero and neg flags as appropriate """
        self.A = self.A & info.value
        self.set_zero_neg(self.A)

    def cmp(self, info):
        """ This instruction compares the contents of the accumulator with
        another memory held value and sets the zero and carry flags as
        appropriate """
        self.compare(self.A, info.value)

    def cld(self, info):
        """ Sets the decimal mode flag to zero """
        self.P = clear_bit(self.P, 3)

    def pha(self, info):
        """ Pushes a copy of the accumulator on to the stack """
        self.SP -= 1
        self.memory[self.SP] = self.A

    def plp(self, info):
        """ Pulls an 8 bit value from the stack and into the processor flags.
        The flags will take on new states as determined by the value pulled """
        self.P = self.memory[self.SP]
        self.P = set_bit(self.P, 5) # This bit is always set
        self.P = clear_bit(self.P, 4)
        self.SP += 1

    def bmi(self, info):
        """ If the negative flag is set then add the relative displacement to
        the program counter to cause a branch to a new location """
        if check_bit(self.P, 7):
            self.P += info.value

    def ora(self, info):
        """ Performs an inclusive OR on the accumulator using the contents of
        a byte of memory, setting the zero and negative flags as appropriate """
        self.A = self.A | info.value
        self.set_zero_neg(self.A)

    def clv(self, info):
        """ Clears the overflow flag """
        self.P = clear_bit(self.P, 6)

    def eor(self, info):
        """ Performs an exclusive OR on the accumulator using the contents of
        a byte of memory, setting the zero and negative flags as appropriate """
        self.A = self.A ^ info.value
        self.set_zero_neg(self.A)

    def adc(self, info):
        """ This instruction adds the contents of a memory location to the
        accumulator together with the carry bit. If overflow occurs the carry
        bit is set, this enables multiple byte addition to be performed """
        prev_A = self.A
        self.A += info.value + check_bit(self.P, 0)

        if (prev_A ^ info.value) & 128 == 0 and (self.A ^ prev_A) & 128 != 0:
            self.P = set_bit(self.P, 6)
        else:
            self.P = clear_bit(self.P, 6)

        if self.A > 255:
            self.P = set_bit(self.P, 0)
            self.A -= 256
        else:
            self.P = clear_bit(self.P, 0)
        self.set_zero_neg(self.A)

    def ldy(self, info):
        """ Loads a byte of memory into the Y register setting the zero and
        negative flags as appropriate """
        self.Y = info.value
        self.set_zero_neg(self.Y)

    def cpy(self, info):
        """ This instruction compares the contents of the Y register with
        another memory held value and sets the zero and carry flags as
        appropriate """
        self.compare(self.Y, info.value)

    def cpx(self, info):
        """ This instruction compares the contents of the X register with
        another memory held value and sets the zero and carry flags as
        appropriate """
        self.compare(self.X, info.value)

instr_functions = [
    "BRK", CPU.ora, "KIL", "SLO", CPU.nop, CPU.ora, "ASL", "SLO",
    CPU.php, CPU.ora, "ASL", "ANC", CPU.nop, CPU.ora, "ASL", "SLO",
    CPU.bpl, CPU.ora, "KIL", "SLO", CPU.nop, CPU.ora, "ASL", "SLO",
    CPU.clc, CPU.ora, CPU.nop, "SLO", CPU.nop, CPU.ora, "ASL", "SLO",
    CPU.jsr, CPU.and_, "KIL", "RLA", CPU.bit, CPU.and_, "ROL", "RLA",
    CPU.plp, CPU.and_, "ROL", "ANC", CPU.bit, CPU.and_, "ROL", "RLA",
    CPU.bmi, CPU.and_, "KIL", "RLA", CPU.nop, CPU.and_, "ROL", "RLA",
    CPU.sec, CPU.and_, CPU.nop, "RLA", CPU.nop, CPU.and_, "ROL", "RLA",
    "RTI", CPU.eor, "KIL", "SRE", CPU.nop, CPU.eor, "LSR", "SRE",
    CPU.pha, CPU.eor, "LSR", "ALR", CPU.jmp, CPU.eor, "LSR", "SRE",
    CPU.bvc, CPU.eor, "KIL", "SRE", CPU.nop, CPU.eor, "LSR", "SRE",
    "CLI", CPU.eor, CPU.nop, "SRE", CPU.nop, CPU.eor, "LSR", "SRE",
    CPU.rts, CPU.adc, "KIL", "RRA", CPU.nop, CPU.adc, "ROR", "RRA",
    CPU.pla, CPU.adc, "ROR", "ARR", CPU.jmp, CPU.adc, "ROR", "RRA",
    CPU.bvs, CPU.adc, "KIL", "RRA", CPU.nop, CPU.adc, "ROR", "RRA",
    CPU.sei, CPU.adc, CPU.nop, "RRA", CPU.nop, CPU.adc, "ROR", "RRA",
    CPU.nop, CPU.sta, CPU.nop, "SAX", "STY", CPU.sta, CPU.stx, "SAX",
    "DEY", CPU.nop, "TXA", "XAA", "STY", CPU.sta, CPU.stx, "SAX",
    CPU.bcc, CPU.sta, "KIL", "AHX", "STY", CPU.sta, CPU.stx, "SAX",
    "TYA", CPU.sta, "TXS", "TAS", "SHY", CPU.sta, "SHX", "AHX",
    CPU.ldy, CPU.lda, CPU.ldx, "LAX", CPU.ldy, CPU.lda, CPU.ldx, "LAX",
    "TAY", CPU.lda, "TAX", "LAX", CPU.ldy, CPU.lda, CPU.ldx, "LAX",
    CPU.bcs, CPU.lda, "KIL", "LAX", CPU.ldy, CPU.lda, CPU.ldx, "LAX",
    CPU.clv, CPU.lda, "TSX", "LAS", CPU.ldy, CPU.lda, CPU.ldx, "LAX",
    CPU.cpy, CPU.cmp, CPU.nop, "DCP", CPU.cpy, CPU.cmp, "DEC", "DCP",
    "INY", CPU.cmp, "DEX", "AXS", CPU.cpy, CPU.cmp, "DEC", "DCP",
    CPU.bne, CPU.cmp, "KIL", "DCP", CPU.nop, CPU.cmp, "DEC", "DCP",
    CPU.cld, CPU.cmp, CPU.nop, "DCP", CPU.nop, CPU.cmp, "DEC", "DCP",
    CPU.cpx, "SBC", CPU.nop, "ISC", CPU.cpx, "SBC", "INC", "ISC",
    "INX", "SBC", CPU.nop, "SBC", CPU.cpx, "SBC", "INC", "ISC",
    CPU.beq, "SBC", "KIL", "ISC", CPU.nop, "SBC", "INC", "ISC",
    CPU.sed, "SBC", CPU.nop, "ISC", CPU.nop, "SBC", "INC", "ISC"
]
