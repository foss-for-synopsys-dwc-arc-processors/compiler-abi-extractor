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
            "char": [bytes([70 + i]) for i in range(16)],
            "signed char": [-i - 21 for i in range(16)],
            "unsigned char": [i + 21 for i in range(16)],
            "int": [-1001 - i for i in range(16)],
            "unsigned int": [1001 + i for i in range(16)],
            "short": [-1001 - i for i in range(16)],
            "unsigned short": [1001 + i for i in range(16)],
            "long": [-1142773077, -1159710506, -1172818702, -1175020290,
                     -1230727382, -1379698938, -1407617162, -1419251393,
                     -1472002004, -1472881177, -1640139052, -1735560817,
                     -1802321509, -1869587600, -1898404909, -1914130792],
            "unsigned long": [1142773077, 1159710506, 1172818702,
                              1175020290, 1230727382, 1379698938,
                              1407617162, 1419251393, 1472002004,
                              1472881177, 1640139052, 1735560817,
                              1802321509, 1869587600, 1898404909,
                              1914130792],
            "long long": [-2137669863270891229, -2522397642985803419,
                          -3706416192938149415, -4458567212862610246,
                          -4953996811516743886, -5008791413612552904,
                          -5263960921296054470, -5659179722960875904,
                          -6666311942245141952, -6632755221326625823,
                          -6912806153521086601, -7120938963231193120,
                          -7468639571267450817, -7939933891726071822,
                          -8608066631949685570, -8957140373517805385],
            "unsigned long long": [2137669863270891229, 2522397642985803419,
                                   3706416192938149415, 4458567212862610246,
                                   4953996811516743886, 5008791413612552904,
                                   5263960921296054470, 5659179722960875904,
                                   6666311942245141952, 6632755221326625823,
                                   6912806153521086601, 7120938963231193120,
                                   7468639571267450817, 7939933891726071822,
                                   8608066631949685570, 8957140373517805385],
        }

    def get_datatypes(self, datatype):
        return self.Datatypes[datatype]

class Converter:
    def __init__(self):
        self.set_format()

     # Set format strings for struct packing
    def set_format(self):
        self.Format = {
            "char": "c",
            "signed char": "!i",    #"!b"
            "unsigned char": "!B",
            "short": "!i",          # !h
            "unsigned short": "!I", # !H
            "int": "!i",
            "unsigned int": "!I",
            "long": "!l",
            "unsigned long": "!L",
            "long long": "!q",
            "unsigned long long": "!Q",
            "float": "!f",
            "double": "!d"
        }

    def to_hex(self, datatype, value):
        # Pack the value based on its datatype format and convert it to hex
        packed_value = struct.pack(self.Format[datatype], value)
        hex_value = "0x" + packed_value.hex().lstrip('0')
        return hex_value

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
            hex_value = Converter().to_hex(datatype, number)

            found = False
            for key, val in mapp.items():
                # Check if the value in the map matches the magic number's hex value
                if val == hex_value:
                    if hex_value not in number_keys:
                        number_keys[hex_value] = []
                    # Append the current key (register/stack position) to the list of keys for this hex value
                    number_keys[hex_value].append(key)
                    # Add the key to the list of found magic numbers
                    found_magic_numbers.append(key)
                    found = True

             # If the magic number was not found in its entirety
            if not found:
                hex_value_int = int(hex_value, 16)
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
            if val == hex_str:
                if hex_str not in number_keys:
                    number_keys[hex_str] = []
                number_keys[hex_str].append(key)
                found_magic_numbers.append(key)
                found = True
        return found

    def _split_hex_value(self, hex_value):
        # Split the hexadecimal value into upper and lower 32-bit parts
        upper_part = hex(hex_value >> 32)
        lower_part = hex(hex_value & 0xFFFFFFFF)
        return upper_part, lower_part

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
