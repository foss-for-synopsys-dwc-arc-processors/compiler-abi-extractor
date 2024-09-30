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
