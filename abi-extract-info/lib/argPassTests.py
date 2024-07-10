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

import struct
class RISCV:
    def __init__(self):
        self.Regs = self.get_regs()
        self.Stack = self.get_stack()
        self.Regs_stack = self.Regs + self.Stack

        # self.Stack_pointer
        # self.Pointer_Size
        # self.Banks
        self.Header_info = tuple()


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
            "char": ["46", "47", "48", "49", "4a", "4b", "4c", "4d",
                     "4e", "4f", "50", "51", "52", "53", "54", "55"],
            "int": ["3e9", "3ea", "3eb", "3ec", "3ed", "3ee", "3ef", "3f0",
                    "3f1", "3f2", "3f3", "3f4", "3f5", "3f6", "3f7", "3f8"],
            "double": ["3fe2788cfc6f802a", "3fe62e42fef1fccc", "3fe921fb544486e0",
                       "3ff33ba004f2ccf4", "3ff6a09e667a35e6", "3ff71547652565ef",
                       "3ff921fb6f1c797b", "3ff9e3779b9486e5", "3ffbb67ae85390f7",
                       "4001e3779b97f681", "40026bb1bbb219d9", "400405f4906034f4",
                       "40052a7fa9d43061", "4005bf0a8b12500b", "400921fb54411744",
                       "40094c583ad801da"],
        }

    def get_datatypes(self, datatype):
        return self.Datatypes[datatype]

class Parser:
    def __init__(self):
        self.Target = RISCV()
        self.Result = []

    def read_file(self, file_name):
        # Read the content of the file and split into lines
        with open(file_name, "r") as file:
            return file.read().splitlines()

    def append(self, W):
        self.Result.append(W)

    import sys
    def remove_comments(self, content):
        # Remove the comments from the content
        arr = list()
        for entry in content:
            if "//" not in entry:
                arr.append(entry)

        return arr


    def read_header(self, content):
        header_number = 6
        self.Target.Header_info = content[:header_number]
        del content[:header_number]

        return content

    def mapping(self, content):
    # Create a mapping between the register set and stack to the output content
        reg_map = {}
        for i in range(len(self.Target.Regs_stack)):
            reg_map[self.Target.Regs_stack[i]] = content[i]
        return reg_map

    def find_magic_number(self, mapp, datatype):
        # Retrieve magic numbers for the given datatype
        magic_numbers = Datatypes().get_datatypes(datatype)

        found_magic_numbers = []
        number_keys = {}
        warnings = []

        for number in magic_numbers:
            # Convert each magic number to its hexadecimal representation
            # hex_value = Converter().to_hex(datatype, number)
            hex_value = number
            found = False
            for key, val in mapp.items():
                # Check if the value in the map matches the magic number's hex value
                # if val == hex_value:
                if hex_value in val:
                    if hex_value not in number_keys:
                        number_keys[hex_value] = []
                    # Append the current key (register/stack position) to the list of keys for this hex value
                    number_keys[hex_value].append(key)
                    # Add the key to the list of found magic numbers
                    found_magic_numbers.append(key)
                    found = True

             # If the magic number was not found in its entirety
            if not found:
                # hex_value_int = int(hex_value, 16)
                hex_value_int = hex_value
                # Split the integer hex value into upper and lower parts
                upper_part, lower_part = self._split_hex_value(hex_value_int)
                # Attempt to find and store keys for the upper part of the hex value
                self._find_and_store_keys(mapp, upper_part, number_keys, found_magic_numbers)
                # Attempt to find and store keys for the lower part of the hex value
                self._find_and_store_keys(mapp, lower_part, number_keys, found_magic_numbers)

        # Generate warnings for any duplicate keys found for the same hex value
        warnings.extend(self._generate_warnings(number_keys))

        # Return the list of found magic numbers and any warnings generated
        return found_magic_numbers, warnings

    def _find_and_store_keys(self, mapp, hex_str, number_keys, found_magic_numbers):
        # Find and store keys associated with hexadecimal values in the mapping dictionary.
        found = False
        for key, val in mapp.items():
            if hex_str in val:
                if hex_str not in number_keys:
                    number_keys[hex_str] = []
                number_keys[hex_str].append(key)
                found_magic_numbers.append(key)
                found = True
        return found

    def _split_hex_value(self, hex_value):
        # Split the hexadecimal value into upper and lower 32-bit parts
        first_half  = hex_value[:len(hex_value)//2]
        second_half = hex_value[len(hex_value)//2:]
        return first_half, second_half

    def _generate_warnings(self, number_keys):
        # Generate warnings for any duplicated argument values
        warnings = []
        for num, keys in number_keys.items():
            if len(keys) > 1:
                warnings.append(f"Warning: Argument value '{num}' duplicated at {keys}. Unable to distinguish.")
        return warnings

    def print_magic_numbers(self, found_magic_numbers, warnings, datatype):
        # Append the found magic numbers and any warnings to the result
        self.append(f"- {datatype:25}: ")
        for item in found_magic_numbers:
            self.append(item+ " ")

        self.append("\n")
        if warnings:
            for warning in warnings:
                self.append(warning + "\n")

    def run(self, file_name, datatype):
        # Run the parsing and analysis process
        content = self.read_file(file_name)

        content = self.remove_comments(content)
        contnet = self.read_header(content)

        mapp = self.mapping(content)
        found_magic_numbers, warnings = self.find_magic_number(mapp, datatype)

        self.print_magic_numbers(found_magic_numbers, warnings, datatype)
        return self.Result

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
