#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
The purpose of this class is to create a bit-field test case
to validate the memory layout of bit-fields.

RISC-V ABIs Specification v1.1
 * Chapter 4. C/C++ type details
 ** 4.4 Bit-Fields
"Bit-fields are packed in little-endian fashion.
A bit-field that would span the alignment boundary of its integer type
is padded to begin at the next alignment boundary. For example,
`struct { int x : 10; int y : 12; }` is a 32-bit type with `x` in bits 9-0,
`y` in bits 21-10, and bits 31-22 undefined. By contrast,
`struct { short x : 10; short y : 12; }` is a 32-bit type
with `x` in bits 9-0, `y` in bits 27-16, and bits 31-28 and bits 15-10
undefined."

For int example:

        struct { int x : 10; int y : 12; }

    Lets assign:
        - `x = 0x3FF` (binary: `11 1111 1111`)
        - `y = 0xFFF` (binary: `1111 1111 1111`)

    Since 10 bits + 12 bits < sizeof(int) = 32 bits,
    both `x` and `y` can be stored within a single 32 bit integer.

    With this in mind, the combined bit pattern would be:
                            ___________  _________
                           /     Y     \/    X    \
                00000000 00111111 11111111 11111111
                  0x00     0x3F     0xFF      0xFF

    In little-endian, the memory layout becomes `0xFF` `0xFF` `0x3F` `0x00`


For short example:

        struct { short x : 10; short y : 12; }

     Lets assign:
        - `x = 0x3FF` (binary: `11 1111 1111`)
        - `y = 0xFFF` (binary: `1111 1111 1111`)


    Since 10 bits + 12 bits > sizeof(short) = 16 bits,
    each `x` and `y` needs to be stored in seperated shorts.

    With this in mind, the combined bit pattern would be:
                     ___________         _________
                    /     Y     \       /    X    \
                00001111 11111111 00000011 11111111
                  0x0F     0xFF     0x03     0xFF

    In little-endian, the memory layout becomes `0xFF` `0x03` `0xFF` `0x0F`
"""

class BitFieldGenerator:
    def __init__(self):
        self.result = []
        self.names = []

    def append(self, W):
        self.result.append(W)

    def extend(self, W):
        self.result.extend(W)

    def get_result(self):
        return "\n".join(self.result)

    def generate_includes(self):
        self.append("#include <stdio.h>")
        self.append("#include <stdint.h>")
        self.append("")

    # Convert binary to decimal
    def binary_to_decimal(self, binary_str):
        binary_str = binary_str.replace(" ", "")
        length = len(binary_str)
        decimal_value = 0

        for i in range(length):
            bit = binary_str[length - 1 - i]
            if bit == "1":
                decimal_value += 2 ** i

        return decimal_value

    # Convert decimal to hexa
    def decimal_to_hexa(self, decimal_value):
        if decimal_value == 0:
            return "0"

        hex_value = ""
        hex_digits = "0123456789ABCDEF"

        while decimal_value > 0:
            remainder = decimal_value % 16
            hex_value = hex_digits[remainder] + hex_value
            decimal_value //= 16

        return "0x" + hex_value

    # Extend binary value with `0` to fit in a given datatype size
    def extend_with_zeros(self, binary, dtype):
        # TODO: Change this.
        if dtype == "int":
            sizeof = 32
        elif dtype == "short":
            sizeof = 16

        binary = binary.replace(" ", "")
        length = len(binary)
        if length < sizeof:
            binary = "0" * (sizeof - length) + binary

        return binary

    # Concatenate binary values without adding padding.
    def no_extra_padding(self, bvalues):
        return ''.join(b.replace(" ", "") for b in reversed(bvalues))

    # Add padding to fit each value in their datatype size.
    def extra_padding(self, bvalues, dtype):
        # Extend each binary value and collect them in a list
        extended_bvalues = [self.extend_with_zeros(b, dtype) for b in bvalues[:-1]] + [bvalues[-1]]

        return self.no_extra_padding(extended_bvalues)

    # Add a space between each X bits (X=4 default).
    def format_binary(self, binary_str, value=4):
        # Reverse the string to format from the right
        reversed_str = binary_str[::-1]
        formatted_str = ''

        for i in range(0, len(reversed_str), value):
            formatted_str += reversed_str[i:i+value] + ' '

        # Reverse back and strip the trailing space
        return formatted_str[::-1].strip()

    # Convert binary to hexa
    def binary_to_hexa(self, bvalue):
        # Remove any spaces in the binary value
        bvalue = bvalue.replace(" ", "")

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

    # Add padding to multiple of 4.
    def pad_mult_4(self, binary):
        # Calculate the number of zeros needed
        length = len(binary)
        if length % 4 != 0:
            zeros_to_add = 4 - (length % 4)
            binary = "0" * zeros_to_add + binary

        return binary

    # Convert little endian to big endian.
    def binary_le_to_be(self, le):
        le = le.replace(" ", "")
        le = self.pad_mult_4(le)
        le = self.format_binary(le, 8)
        return " ".join(le.split()[::-1])

    # Generate a name for the datatype.
    def get_name(self, data):
        # Create the initial name from the data types
        base_name = "_".join(i["dtype"] for i in data)

        # Initialize the name to the base name
        name = base_name
        count = 2

        # Check for name collisions and increment count as needed
        while name in self.names:
            name = f"{base_name}_{count}"
            count += 1

        # Add the final name to self.names
        self.names.append(name)
        return name
