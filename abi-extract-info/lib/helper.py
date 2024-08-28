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

def indexes_to_registers(register_names, indexes):
    return [register_names[index] for index in indexes]

# Convert decimal to a fixed-length hexadecimal string.
def decimal_to_hex(decimal, width=2):
    if decimal == 0:
        return "0".zfill(width)

    hex_chars = "0123456789abcdef"
    hex_str = ""

    while decimal > 0:
        remainder = decimal % 16
        hex_str = hex_chars[remainder] + hex_str
        decimal //= 16

    return hex_str.zfill(width)

# Generates a unique hexadecimal value of a given saize, optionally resetting the counter.
def generate_hexa_values_2(sizeof, reset = None):

    # Initialize static variables if they do not exist.
    if not hasattr(generate_hexa_values_2, "used_values"):
        generate_hexa_values_2.used_values = set()

    if not hasattr(generate_hexa_values_2, "i") or reset != None:
        reset_to = reset if reset else 1
        # e.i static int i = 1;
        generate_hexa_values_2.i = reset_to # Initialize the static variable
        generate_hexa_values_2.used_values.clear()


    while True:
        result = ""
        # Generate the hexadecimal string based on current counter.
        for j in range(1, sizeof + 1):
            result += decimal_to_hex(generate_hexa_values_2.i)
            generate_hexa_values_2.i += 1

        # Ensure the hexadecimal value does not start with a 0.
        # The `0` would be ignored by the compiler, leading to unmatching
        # values when validating.
        if result[0] == "0":
            num_str = str(generate_hexa_values_2.i)
            first_digit = num_str[0]
            result = first_digit + result[1:]

        # FIXME Assuming sizeof(int) is 4 bytes; should be dynamic if needed
        sizeof_int = 4

        # When the value is too big to fit in a single register, its likely that
        # the compiler will split it in half. When this happens, we need to ensure
        # that the second half does not also start with a `0`.
        if sizeof == sizeof_int * 2:
            if result[len(result) // 2] == "0":
                result = list(result)
                num_str = str(generate_hexa_values_2.i)
                first_digit = num_str[0]
                result[len(result) // 2] = first_digit
                result = "".join(result)

        # Add generated hexadecimal value to used list.
        if result not in generate_hexa_values_2.used_values:
            generate_hexa_values_2.used_values.add(result)
            break

    # Change this to the `_add` function in hexUtils.
    result = f"0x{result}"

    return result

# Generate a list of unique hexadecimal values.
def generate_hexa_list(length, sizeof, reset = None):
    values = []
    for i in range(length):
        values.append(generate_hexa_values_2(sizeof, reset))
        reset = None

    return values

# Generate a list of unique hexadecimal values based on datatypes.
def generate_hexa_list_from_datatypes(dtypes, Target, reset = None):
    values = []
    for dtype in dtypes:
        sizeof = Target.get_type_details(dtype)["size"]
        values.append(generate_hexa_values_2(sizeof, reset))
        reset = None

    return values
