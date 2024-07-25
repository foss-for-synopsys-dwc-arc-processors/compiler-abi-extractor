#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import os

# Add the compiler and simulator wrappers to the
# PATH environment variable to enable a modular
# approach for invoking various compilers and simulators.
def set_env(cc, sim):
    root_path = os.path.abspath(".")
    wrapper_path = root_path + "/scripts/wrapper/"

    # Set environment variable
    os.environ["PATH"] = wrapper_path + f"/cc/{cc}:" + os.environ["PATH"]
    os.environ["PATH"] = wrapper_path + f"/sim/{sim}:" + os.environ["PATH"]

# Responsible for reading a file and returning its contents.
# This is used by multiple classes.
def read_file(file_name):
    with open(file_name, "r") as file:
        return file.read()

import re
# Responsible for parsing the standard output from the datatype
#  signedness/size/align test case for use in other test cases.
# This information will be stored in 'type_details' in the 'TargetArch' class.
def parse_type_info(text):
    lines = text.strip().split('\n')
    type_details = dict()

    for line in lines:
        type_name = re.search(r'^([\w\s\*]+)\s*', line)
        type_name = type_name.group(1) if type_name else None
        type_name = type_name.strip()

        signedness = re.search(r'signedness: (\d+)', line).group(1)
        size = re.search(r'size: (\d+)', line).group(1)
        align = re.search(r'align: (\d+)', line).group(1)

        type_details[type_name] = {
            "signedness": int(signedness),
            "size": int(size),
            "align": int(align)
        }

    return type_details

# Create a mapping between the register set and their values.
def make_mapping(regs, values):
    reg_values = dict()
    for index, reg in enumerate(regs):
        reg_values[reg] = values[index]
    return reg_values

# Create a list of hexadecimal values according to the datatype size.
# Give the following example:
# | Datatype |  Size   | hexadecimal value  |
# +----------+---------+--------------------+
# | Char     | 1 byte  | 0x12               |
# | Short    | 2 byte  | 0x1234             |
# | Int      | 4 bytes | 0x12345678         |
# | Double   | 8 bytes | 0x1234567890abcdef |
def generate_hexa_values(Target, datatype, count):
    size = Target.get_type_details(datatype)["size"]
    values_list = []
    hex_digits = "1234567890abcdef"  # Hexadecimal digits

    # This was being used for the 'long double'..
    # Result: '0x0123456789abcdeffedcba9876543210'
    if size == 16:
        # Reverse the hex digits
        reversed_hex_digits = hex_digits[::-1]
        # Append the reversed hex digits
        hex_digits = hex_digits + reversed_hex_digits

    # Create a hexadecimal string with size*2 digits
    value = hex_digits[:(size * 2)]
    value = "0x" + value

    # Generate the list of hexadecimal string values
    values_list = [value] * count

    return values_list
