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

def cleanup(folder="tmp/"):
    # Check if the folder exists
    if os.path.exists(folder):
        # Loop through the directory and remove contents
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    # Remove file
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

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

import random
def generate_binary_value(sizeof):
    # Initialize static variable
    if not hasattr(generate_binary_value, "used_values"):
        generate_binary_value.used_values = []

    # The most significant bit must be 1. So we
    # subtract 1 in its sizeof and add 1 later.
    length = sizeof - 1

    bvalue = "".join(random.choice("01") for _ in range(length))
    while bvalue in generate_binary_value.used_values:
        bvalue = "".join(random.choice("01") for _ in range(length))

    generate_binary_value.used_values.append(bvalue)
    bvalue = f"1{bvalue}"

    return bvalue

# Convert binary to hexa
def binary_to_hexa(bvalue):
    # Remove any spaces in the binary value
    bvalue = bvalue.replace(" ", "")

    # Remove undefined digits
    bvalue = bvalue.replace("N", "0")

    # Ensure the binary value is a valid length (multiple of 4)
    while len(bvalue) % 4 != 0:
        bvalue = "0" + bvalue

    # Create a mapping of binary to hexadecimal
    binary_to_hex_map = {
        '0000': '0', '0001': '1', '0010': '2', '0011': '3',
        '0100': '4', '0101': '5', '0110': '6', '0111': '7',
        '1000': '8', '1001': '9', '1010': 'A', '1011': 'B',
        '1100': 'C', '1101': 'D', '1110': 'E', '1111': 'F'
    }

    hvalue = ""
    # Process each 4-bit chunk
    for i in range(0, len(bvalue), 4):
        four_bits = bvalue[i:i + 4]
        hvalue += binary_to_hex_map[four_bits]

    return "0x" + hvalue

# Convert hexadecimal to binary with leading zeros removed
def hexa_to_binary(hvalue):
    # Remove the '0x' prefix if present
    if hvalue.startswith("0x"):
        hvalue = hvalue[2:]

    # Create a mapping of hexadecimal to binary
    hex_to_binary_map = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011',
        '4': '0100', '5': '0101', '6': '0110', '7': '0111',
        '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
        'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
    }

    bvalue = ""
    # Process each hexadecimal digit
    for digit in hvalue.upper():
        bvalue += hex_to_binary_map[digit]

    # Remove leading zeros
    bvalue = bvalue.lstrip('0')

    # Return '0' if the result is an empty string (e.g., for input '0x0')
    return bvalue if bvalue else '0'
