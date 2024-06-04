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

class Datatypes:
    def __init__(self):
        self.Datatypes = {}
        self.set_datatypes()

    def set_datatypes(self):
        self.Datatypes = {
            "char": range(70, 86),
            "int": range(1001, 1017),
            "short": range(1001, 1017),
            "long":  range(1001, 1017),
            "float": [
                1148862628,1148879176,1148895724,1148912271,
                1148928819,1148945367,1148961915,1148978463,
                1148995011,1149011558,1149028106,1149044654,
                1149061202,1149077750,1149094298,1149110845
            ],
            "char,short": [i for pair in zip(range(71, 79), range(1001, 1009)) for i in pair]
        }

    def get_datatypes(self, datatype):
        return self.Datatypes[datatype]

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

    # Create a mapping between the register set and
    # stack to the output content
    def mapping(self, content):
        mapp = {}
        for i in range(len(self.Target.Regs_stack)):
            mapp[self.Target.Regs_stack[i]] = content[i]
        return mapp

    # Identify the magic numbers (1001 to 1017)
    # If duplicate magic numbers are found,
    # a warning is issued.
    def find_magic_number(self, mapp, datatype):
        # magic_numbers = range(1001, 1018)
        magic_numbers = Datatypes().get_datatypes(datatype)
        # magic_numbers = range(1001, 1018)
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


    def run(self, file_name, datatype):
        content = self.read_file(file_name)
        mapp = self.mapping(content)
        found_magic_numbers, warnings = self.find_magic_number(mapp, datatype)

        self.print_magic_numbers(found_magic_numbers, warnings, datatype)
        return self.Result

    # Append the results and return it.
    def print_magic_numbers(self, found_magic_numbers, warnings, datatype):
        self.append(f"{datatype}: ")
        for item in found_magic_numbers:
            self.append(item+ " ")

        self.append("\n")
        if warnings:
            for warning in warnings:
                self.append(warning + "\n")
def header():
    return ["16 Argument Passing test:\n"]

def parser(file_name, datatype):
    return Parser().run(file_name, datatype)

import sys
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 argPassTest.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]
    result = Parser().run(file_name)
    print("".join(result), end="")
