#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This script is designed to identify specific "magic numbers"
within a range (from 1001 to 1017), determining how argument
values are passed, whether through registers, stack, or both.
It analyzes a register and stack (up to 128 bytes) dump values
as input and matches these magic numbers to appropriate
labels (registers, and/or stack), considering the sequecne
in which they appear.

Additionally, it checks for any duplicate occurrences of
magic numbers, which might occur if a magic number is generated
by the compiler and stored in a register, leading to potential
conflicts. When duplicates are detected, it issues a warning
alerting that was unable to distinct.
"""

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

    # Identify the magic numbers (1001 to 1017)
    # If duplicate magic numbers are found,
    # a warning is issued.
    def find_magic_number(self, mapp):
        magic_numbers = set(range(1001, 1018))
        found_magic_numbers = []
        number_keys = {num: [] for num in magic_numbers}
        warnings = []

        for number in magic_numbers:
            for key, val in mapp.items():
                if int(val) == number:
                    number_keys[number].append(key)
                    found_magic_numbers.append(key)

        for num, keys in number_keys.items():
            if len(keys) > 1:
                warnings.append(f"Warning: Argument value '{num}' duplicated at {keys}. Unable to distinct.")

        return found_magic_numbers, warnings

class Parser:
    def __init__(self):
        self.Target = RISCV()
        self.Result = []

    def read_file(self, file_name):
        with open(file_name, "r") as file:
            content = file.read().splitlines()
        return content

    def append(self, W):
        self.Result.append(W)

    def run(self, file_name):
        content = self.read_file(file_name)
        mapp = self.Target.mapping(content)
        found_magic_numbers, warnings = self.Target.find_magic_number(mapp)

        self.print_magic_numbers(found_magic_numbers, warnings)
        return self.Result

    # Append the results and return it.
    def print_magic_numbers(self, found_magic_numbers, warnings):
        self.append("Argument Passing layout - 17 arguments:\n")
        for item in found_magic_numbers:
            self.append(item + "\n")


        if warnings:
            for warning in warnings:
                self.append(warning + "\n")

def parser(file_name):
    Parser().run(file_name)
    return Parser().run(file_name)

import sys
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 argPassTest.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]
    result = Parser().run(file_name)
    print("".join(result), end="")
