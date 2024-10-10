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

    The memory layout is `0x00` `0x3F` `0xFF` `0xFF`


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

    The memory layout is `0x0F` `0xFF` `0x03` `0xFF`
"""

from lib import helper

class BitFieldGenerator:
    def __init__(self, Target):
        self.Target = Target
        self.result = []
        self.names = []
        self.data = {
            "short": [(10, 12),  (6,  8)],
            "int":   [(18, 19), (10, 12)],
        }

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

    # Extend binary value with `N` to fit in a given datatype size
    def extend_with_undefined(self, bvalue, dtype):
        sizeof = self.Target.get_type_details(dtype)["size"]
        sizeof *= 8 # FIXME: Convert bytes to bits.
        bvalue = bvalue.replace(" ", "")
        length = len(bvalue)
        if length < sizeof:
            bvalue = "N" * (sizeof - length) + bvalue

        return bvalue

    # Concatenate binary values without adding padding.
    def no_extra_padding(self, bvalues):
        bvalue = ''.join(b.replace(" ", "") for b in reversed(bvalues))
        return self.pad_mult_4(bvalue)

    # Add padding to fit each value in their datatype size.
    def extra_padding(self, bvalues, dtype):
        # Extend each binary value and collect them in a list
        extended_bvalues = [self.extend_with_undefined(b, dtype) for b in bvalues[:-1]] + [bvalues[-1]]

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

    # Add padding to multiple of 4.
    def pad_mult_4(self, bvalue):
         # Remove any spaces in the binary value
        bvalue = bvalue.replace(" ", "")

        # Calculate the number of zeros needed
        # e.g
        # bvalue = 1010101010
        # return NN1010101010
        length = len(bvalue)
        if length % 4 != 0:
            zeros_to_add = 4 - (length % 4)
            bvalue = "N" * zeros_to_add + bvalue

        return bvalue

    # Create a mask from a binary value.
    def create_mask(self, bvalue):
        # e.g
        # bvalue = NNNN 1101 1011 0110 NNNN NN10 1010 1010
        # bmask  = 0000 1111 1111 1111 0000 0011 1111 1111
        bmask = bvalue.replace("0", "1")
        bmask = bmask.replace("N", "0")

        return bmask

    # Convert binary value from little endian to big endian.
    def little_to_big_endian(self, bvalue):
        # (e.g) bvalue =      1101 1011 0110 NNNN NN10 1010 1010
        #   bvalue_pad = NNNN 1101 1011 0110 NNNN NN10 1010 1010
        bvalue_pad = self.pad_mult_4(bvalue)

        # Add a space between each 8 bits.
        # (e.g) le = NNNN1101 10110110 NNNNNN10 10101010
        bvalue = self.format_binary(bvalue_pad, 8)

        # (e.g) return 10101010 NNNNNN10 10110110 NNNN1101
        return "".join(bvalue.split()[::-1])

    # Generate a name for the datatype.
    def get_name(self, dtype):
        # Create the initial name from the data type
        base_name = f"{dtype.replace(' ', '_')}"

        # Initialize the name to the base name
        count = 0
        name = f"{base_name}_{count}"

        # Check for name collisions and increment count as needed
        while name in self.names:
            name = f"{base_name}_{count}"
            count += 1

        # Add the final name to self.names
        self.names.append(name)
        return name

    # Split binary value as upper and lower bits.
    def split_upper_lower(self, bvalue, bits=32):
        upper_length = len(bvalue) - bits
        return bvalue[:upper_length], bvalue[-bits:]

    def generate_struct_union(self, name, dtype, bitfields):
        # e.g
        # union union_short_0 {
        #   struct {
        #       unsigned short x0 : 10;
        #       unsigned short x1 : 12;
        #   } s;
        #   unsigned long long values[2];
        # };
        self.append(f"union union_{name} {{")
        self.append(f"  struct {{")
        for i, bfield in enumerate(bitfields):
            self.append(f"    unsigned {dtype} x{i} : {bfield};")
        self.append("  } s;")
        self.append(f" unsigned long long values[{len(bitfields)}];")
        self.append("};")

    def generate_calculate(self, name, dtype, bitfields):
        # e.g
        # void calculate_short_0 (void) {
        self.append(f"void calculate_{name} (void) {{")

        tmp_str = ""
        hvalues = []
        for i, bfield in enumerate(bitfields):
            bvalue = helper.generate_binary_value(bfield)
            hvalue = helper.binary_to_hexa(bvalue)
            tmp_str += f".x{i} = {hvalue}, "
            hvalues.append(hvalue)

        # e.g
        # union union_short_0 test = { .s = { .x = 0x2AA, .y = 0xDB6 } };
        self.append(f"  union union_{name} test = {{ .s = {{ {''.join(tmp_str)} }} }};")

        bfields_sum = sum(bitfields)
        sizeof = self.Target.get_type_details(dtype)["size"]
        sizeof *= 8 # FIXME: Convert bytes to bits.
        # Calculate if greater.
        sign = ">" if bfields_sum > sizeof else "<"

        # e.g
        # printf("short:>:");
        self.append(f'printf("{name}:{sign}:");')

        bvalues = []
        for hvalue in hvalues:
            bvalues.append(helper.hexa_to_binary(hvalue))

        # e.g
        # if ((test.value & 0x3FFFFF) == 0x36DAAA)
        # {
        #   printf("No extra padding.:");
        #   printf("Little-endian.");
        # }
        bvalue_little_endian_no_pad = self.no_extra_padding(bvalues)
        bmask_little_endian_no_pad  = self.create_mask(bvalue_little_endian_no_pad)
        self.append(f"""
    if ((*test.values & {helper.binary_to_hexa(bmask_little_endian_no_pad)}) == {helper.binary_to_hexa(bvalue_little_endian_no_pad)})
    {{
        printf("No extra padding.:");
        printf("Little-endian.");
    }}""")

        # e.g
        # else if ((test.value & 0xFFFF3F) == 0xAADA36)
        # {
        #   printf("No extra padding.:");
        #   printf("Big endian.");
        # }
        bvalue_big_endian_no_pad = self.little_to_big_endian(bvalue_little_endian_no_pad)
        bmask_big_endian_no_pad  = self.create_mask(bvalue_big_endian_no_pad)
        self.append(f"""
    if ((*test.values & {helper.binary_to_hexa(bmask_big_endian_no_pad)}) == {helper.binary_to_hexa(bvalue_big_endian_no_pad)})
    {{
        printf("No extra padding.:");
        printf("Big-endian.");
    }}""")

        # e.g
        # else if ((test.value & FFF03FF) == 0xDB602AA)
        # {
        #   printf("Extra padding.:");
        #   printf("Little endian.");
        # }
        bvalue_little_endian_pad = self.extra_padding(bvalues, dtype)
        bmask_little_endian_pad  = self.create_mask(bvalue_little_endian_pad)
        self.append(f"""
    if ((*test.values & {helper.binary_to_hexa(bmask_little_endian_pad)}) == {helper.binary_to_hexa(bvalue_little_endian_pad)})
    {{
        printf("Extra padding.:");
        printf("Little-endian.");
    }}""")

        # e.g
        # else if ((test.value & 0xFF03FF0F) == 0xAA02B6D)
        # {
        #   printf("Extra padding.:");
        #   printf("Big endian.");
        # }
        bvalue_big_endian_pad = self.little_to_big_endian(bvalue_little_endian_pad)
        bmask_big_endian_pad  = self.create_mask(bvalue_big_endian_pad)
        self.append(f"""
    if ((*test.values & {helper.binary_to_hexa(bmask_big_endian_pad)}) == {helper.binary_to_hexa(bvalue_big_endian_pad)})
    {{
        printf("Extra padding.:");
        printf("Big-endian.");
    }}""")

        self.append('printf("\\n");')
        self.append("}")

    def generate_calculate_for_split(self, name, dtype, bitfields):
        # e.g
        # void calculate_short_0 (void) {
        self.append(f"void calculate_{name} (void) {{")

        tmp_str = ""
        hvalues = []
        for i, bfield in enumerate(bitfields):
            bvalue = helper.generate_binary_value(bfield)
            hvalue = helper.binary_to_hexa(bvalue)
            tmp_str += f".x{i} = {hvalue}, "
            hvalues.append(hvalue)

        # e.g
        # union union_short_0 test = { .s = { .x = 0x2AA, .y = 0xDB6 } };
        self.append(f"  union union_{name} test = {{ .s = {{ {''.join(tmp_str)} }} }};")

        bfields_sum = sum(bitfields)
        sizeof = self.Target.get_type_details(dtype)["size"]
        sizeof *= 8 # FIXME: Convert bytes to bits.
        # Calculate if greater.
        sign = ">" if bfields_sum > sizeof else "<"

        # e.g
        # printf("short:>:");
        self.append(f'printf("{name}:{sign}:");')

        bvalues = []
        for hvalue in hvalues:
            bvalues.append(helper.hexa_to_binary(hvalue))

        self.append("""
    unsigned long long lower_bits = (*(test.values + 0) & 0xFFFFFFFF);
    unsigned long long upper_bits = ((*(test.values + 0) >> 32) & 0xFFFFFFFF);
""")

        # e.g
        # if ((lower_bits & 0x3FFFFF) == 0x36DAAA)
        # {
        #   printf("No extra padding.:");
        #   printf("Little-endian.");
        # }
        bvalue_little_endian_no_pad = self.no_extra_padding(bvalues)
        bmask_little_endian_no_pad  = self.create_mask(bvalue_little_endian_no_pad)

        bvalue_upper, bvalue_lower = self.split_upper_lower(bvalue_little_endian_no_pad)
        bmask_upper, bmask_lower  = self.split_upper_lower(bmask_little_endian_no_pad)

        self.append(f"""
    if ((lower_bits & {helper.binary_to_hexa(bmask_lower)}) == {helper.binary_to_hexa(bvalue_lower)} &&
        (upper_bits & {helper.binary_to_hexa(bmask_upper)}) == {helper.binary_to_hexa(bvalue_upper)})
    {{
        printf("No extra padding.:");
        printf("Little-endian.");
    }}""")

        # e.g
        # else if ((test.value & 0xFFFF3F) == 0xAADA36)
        # {
        #   printf("No extra padding.:");
        #   printf("Big endian.");
        # }
        bvalue_big_endian_no_pad = self.little_to_big_endian(bvalue_little_endian_no_pad)
        bmask_big_endian_no_pad  = self.create_mask(bvalue_big_endian_no_pad)

        bvalue_upper, bvalue_lower = self.split_upper_lower(bvalue_big_endian_no_pad)
        bmask_upper, bmask_lower  = self.split_upper_lower(bmask_big_endian_no_pad)

        self.append(f"""
    if ((lower_bits & {helper.binary_to_hexa(bmask_lower)}) == {helper.binary_to_hexa(bvalue_lower)} &&
        (upper_bits & {helper.binary_to_hexa(bmask_upper)}) == {helper.binary_to_hexa(bvalue_upper)})
    {{
        printf("No extra padding.:");
        printf("Big-endian.");
    }}""")

        self.append("""
    lower_bits = (*(test.values + 0) & 0xFFFFFFFFFFFFFFFF);
    upper_bits = (*(test.values + 1) & 0xFFFFFFFFFFFFFFFF);
""")

        # e.g
        # else if ((test.value & FFF03FF) == 0xDB602AA)
        # {
        #   printf("Extra padding.:");
        #   printf("Little endian.");
        # }
        bvalue_little_endian_pad = self.extra_padding(bvalues, dtype)
        bmask_little_endian_pad  = self.create_mask(bvalue_little_endian_pad)

        bvalue_upper, bvalue_lower = self.split_upper_lower(bvalue_little_endian_pad, 64)
        bmask_upper, bmask_lower  = self.split_upper_lower(bmask_little_endian_pad, 64)
        self.append(f"""
    if ((lower_bits & {helper.binary_to_hexa(bmask_lower)}) == {helper.binary_to_hexa(bvalue_lower)} &&
        (upper_bits & {helper.binary_to_hexa(bmask_upper)}) == {helper.binary_to_hexa(bvalue_upper)})
    {{
        printf("Extra padding.:");
        printf("Little-endian.");
    }}""")

        # e.g
        # else if ((test.value & 0xFF03FF0F) == 0xAA02B6D)
        # {
        #   printf("Extra padding.:");
        #   printf("Big endian.");
        # }
        bvalue_big_endian_pad = self.little_to_big_endian(bvalue_little_endian_pad)
        bmask_big_endian_pad  = self.create_mask(bvalue_big_endian_pad)

        _, bvalue_lower = self.split_upper_lower(bvalue_big_endian_pad, 64)
        _, bmask_lower  = self.split_upper_lower(bmask_big_endian_pad, 64)
        self.append(f"""
    if ((lower_bits & {helper.binary_to_hexa(bmask_lower)}) == {helper.binary_to_hexa(bvalue_lower)})
    {{
        printf("Extra padding.:");
        printf("Big-endian.");
    }}""")

        self.append('printf("\\n");')
        self.append("}")

    def generate_main(self):
        self.append("int main (void) {")
        self.extend(f'  calculate_{name}();' for name in self.names)
        self.append(f"  return 0;")
        self.append("}")

    def generate(self):
        self.generate_includes()
        for dtype, data in self.data.items():
            for bitfields in data:
                name = self.get_name(dtype)
                self.generate_struct_union(name, dtype, bitfields)
                self.generate_calculate(name, dtype, bitfields)

        self.generate_main()
        return self.get_result()

def generate(Target):
    return BitFieldGenerator(Target).generate()

if __name__ == "__main__":
    print(generate())
