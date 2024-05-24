# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

class RISCV:
    def __init__(self):
        self.Regs = self.get_regs()
        self.Stack = self.get_stack()
        self.Regs_stack = self.Regs + self.Stack

    # Return RISCV Register Set
    def get_regs(self):
        return [
            "zero", "ra", "sp", "gp", "tp",
            "t0", "t1", "t2", "s0", "s1",
            "a0", "a1", "a2", "a3", "a4",
            "a5", "a6", "a7", "s2", "s3",
            "s4", "s5", "s6", "s7", "s8",
            "s9", "s10", "s11", "t3", "t4",
            "t5", "t6"
        ]

    # Return stack up to 128 byes
    def get_stack(self):
        stack = []
        for i in range(32):
            stack.append(f"sp+({i * 4})")
        return stack

    # Create a mapping between the register set and
    # stack to the output content
    def mapping(self, content):
        mapp = {}
        for i in range(len(self.Regs_stack)):
            mapp[self.Regs_stack[i]] = content[i]
        return mapp

    # Identify the magic numbers (1001 to 1017) to
    # determine how the argument values were
    # passed (registers, stack, or both)
    def find_magic_number(self, mapp):
        magic_numbers = set(range(1001, 1018))
        found_magic_numbers = []
        for key, val in mapp.items():
            if int(val) in magic_numbers:
                found_magic_numbers.append(key)
        return found_magic_numbers

class Parser:
    def __init__(self):
        self.Riscv = RISCV()
        self.Result = []

    def read_file(self, file_name):
        with open(file_name, "r") as file:
            content = file.read().splitlines()
        return content

    def append(self, W):
        self.Result.append(W)

    def run(self, file_name):
        content = self.read_file(file_name)
        mapp = self.Riscv.mapping(content)
        found_magic_numbers = self.Riscv.find_magic_number(mapp)

        self.print_magic_numbers(found_magic_numbers)
        return self.Result

    # Append the results and return it.
    def print_magic_numbers(self, found_magic_numbers):
        self.append("Argument Passing layout - 17 arguments:")
        for item in found_magic_numbers:
            self.append("\n" + item)

        self.append("\n")

def parser(file_name):
    Parser().run(file_name)
    return Parser().run(file_name)
