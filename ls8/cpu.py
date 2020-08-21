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
        self.CMP = 0b10100111
        self.lflag = 0
        self.gflag = 0
        self.eflag = 0
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.JGE = 0b01011010
        self.JGT = 0b01010111
        self.JLE = 0b01011001
        self.JLT = 0b01011000
        self.AND = 0b10101000
        self.OR = 0b10101010
        self.XOR = 0b10101011
        self.NOT = 0b01101001
        self.SHL = 0b10101100
        self.SHR = 0b10101101
        self.MOD = 0b10100100


 

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
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] ^= 0b11111111 
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
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
                # self.op_size = (cmd >> 6) + 1
            
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

            # CMP
            elif cmd == self.CMP:
                if self.reg[operand_a] < self.reg[operand_b]:
                    self.lflag = 1
                    self.gflag = 0
                    self.eflag = 0
                elif self.reg[operand_a] > self.reg[operand_b]:
                    self.gflag = 1
                    self.lflag = 0
                    self.eflag = 0
                elif self.reg[operand_a] == self.reg[operand_b]:
                    self.eflag = 1
                    self.gflag = 0
                    self.lflag = 0
                self.op_size = (cmd >> 6) + 1
 
            # JMP
            elif cmd == self.JMP:
                self.pc = self.reg[operand_a]
                self.op_size = 0
            
            # JEQ
            elif cmd == self.JEQ:
                if self.eflag == 1:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1

            # JNE
            elif cmd == self.JNE:
                if self.eflag == 0:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1

            # JGE
            elif cmd == self.JGE:
                if self.eflag == 1 or self.gflag == 1:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1

            # JGT
            elif cmd == self.JGT:
                if self.gflag == 1:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1

            # JLE
            elif cmd == self.JLE:
                if self.eflag == 1 or self.lflag == 1:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1

            # JLT
            elif cmd == self.JLT:
                if self.lflag == 0:
                    self.pc = self.reg[operand_a]
                    self.op_size = 0
                else:
                    self.op_size = (cmd >> 6) + 1
            
            # AND
            elif cmd == self.AND:
                self.alu("AND", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # OR
            elif cmd == self.OR:
                self.alu("OR", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # XOR
            elif cmd == self.XOR:
                self.alu("XOR", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # NOT
            elif cmd == self.NOT:
                self.alu("NOT", operand_a)
                self.op_size = (cmd >> 6) + 1

            # SHL
            elif cmd == self.SHL:
                self.alu("SHL", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # SHR
            elif cmd == self.SHR:
                self.alu("SHR", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            # MOD
            elif cmd == self.MOD:
                self.alu("MOD", operand_a, operand_b)
                self.op_size = (cmd >> 6) + 1

            
            self.pc += self.op_size
