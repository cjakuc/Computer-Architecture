"""CPU functionality."""

import sys
import os
dirpath = os.path.dirname(os.path.abspath(__file__))

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.op_size = None
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.ADD = 0b10100000
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        # self.SHL = 0b10101100
        # self.SHR = 0b10101101

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, val):
        self.ram[address] = val
        return None

    def load(self, filename):
        """Load a program into memory."""
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    n = comment_split[0].strip()
                    if n == '':
                        continue
                    value = int(n, 2)
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print(f"{sys.agrv[0]}: {filename} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        self.reg[self.sp] = 0xf4

        while running:
            cmd = self.ram[self.pc]
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # HLT
            if cmd == self.HLT:
                running = False
                self.op_size = (cmd >> 6) + 1
            
            # LDI
            elif cmd == self.LDI:
                self.reg[operand_a] = operand_b
                # self.pc += 3
                self.op_size = (cmd >> 6) + 1

            # PRN
            elif cmd == self.PRN:
                # self.pc += 2
                print(self.reg[operand_a])
                self.op_size = (cmd >> 6) + 1

            # ADD
            elif cmd == self.ADD:
                self.alu("ADD", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # MUL
            elif cmd == self.MUL:
                # self.pc += 3
                self.alu("MUL", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # PUSH
            elif cmd == self.PUSH:
                val = self.reg[operand_a]
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = val
                # self.pc += 2

                self.op_size = (cmd >> 6) + 1


            # POP
            elif cmd == self.POP:
                val = self.ram[self.reg[self.sp]]
                self.reg[operand_a] = val
                self.reg[self.sp] += 1
                self.op_size = (cmd >> 6) + 1

            # CALL
            elif cmd == self.CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = (self.pc + 2)

                reg_index = self.ram[self.pc + 1]
                self.pc = self.reg[reg_index]

                self.op_size = 0

            # RET
            elif cmd == self.RET:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1

                self.op_size = 0

            # SHL
            # elif cmd == self.SHL:
            #     self.reg[operand_a] <<= self.reg[operand_b]

            # SHR
            # elif cmd == self. SHR:
            #     self.reg[operand_a] >>= self.reg[operand_b]
            
            self.pc += self.op_size
