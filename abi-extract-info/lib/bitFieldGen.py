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


    The resulting hexadecimal value `0x003FFFFF` is in big-endian format,
    so we need to convert it to little-endian.

    In little-endian, the value becomes `0xFFFF3F00` (`0xFF` `0xFF` `0x3F` `0x00`)


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

    The resulting hexadecimal value `0x0FFF03FF` is in big-endian format, so we need to
    convert it to little-endian.

    In little-endian, the value becomes `0xFF03FF0F` (`0xFF` `0x03` `0xFF` `0x0F`)
"""

class BitFieldGenerator:
    def __init__(self):
        self.result = []
        self.structs = [
            { "x": ("int", 10), "y": ("int", 12) },
            { "x": ("short", 10), "y": ("short", 12) }
        ]

    def append(self, text):
        self.result.append(text)

    def get_result(self):
        return "\n".join(self.result)

    def generate_includes(self):
        self.append("#include <stdio.h>")
        self.append("#include <stdint.h>")
        self.append("")

    # Generate a struct name based on field types.
    def generate_struct_name(self, fields):
        types = "_".join([value[0] for value in fields.values()])
        return f"{types}_bitfield"

    # Generate a comment describing the bitfields.
    def generate_bitfield_comment(self, fields):
        types = " ".join([value[0] for value in fields.values()])
        return f"/* Structure with {types} bitfields. */"

    # Calculate the maximum value for a given bit width.
    def calculate_max_value(self, bit_width):
        return (1 << bit_width) - 1

    # Format the hexadecimal value without unnecessary leading zeros.
    def format_hex(self, value):
        return f"{value:X}"

    # Generate structures.
    def generate_structs(self):
        for struct in self.structs:
            struct_name = self.generate_struct_name(struct)
            comment = self.generate_bitfield_comment(struct)

            self.append(f"{comment}")
            self.append(f"struct {struct_name} {{")

            for field, (field_type, bit_width) in struct.items():
                self.append(f"    unsigned {field_type} {field} : {bit_width};")

            self.append("};")

    # Generate function to print the bytes of a memory address.
    def generate_print_bytes(self):
        self.append("""
/* Function to print bytes of a memory address. */
void print_bytes(void *ptr, size_t size) {
    uint8_t *byte_ptr = (uint8_t *)ptr;
    size_t i;
    for (i = 0; i < size; i++)
    {
        printf("0x%02X ", byte_ptr[i]);
    }
    printf("\\n");
}
""")

    # Generate the main function for testing the structures.
    def generate_main(self):
        self.append("int main (void) {")

        self.append("    printf(\"Bit-field test:\\n\");")
        for struct in self.structs:
            struct_name = self.generate_struct_name(struct)
            field_type_name = "_".join([value[0] for value in struct.values()])

            self.append(f"    /* Testing the {field_type_name}_bitfield structure. */")
            self.append(f"    struct {struct_name} test_{field_type_name} = {{0}};")

            assignments = []
            values = []

            for field, (field_type, bit_width) in struct.items():
                max_value = self.calculate_max_value(bit_width)
                formatted_value = self.format_hex(max_value)
                assignments.append(f"    test_{field_type_name}.{field} = 0x{formatted_value}; /* Max value for {bit_width} bits. */")
                values.append(f"{field}=0x{formatted_value}")

            # Add assignments and printf statement
            self.append("\n".join(assignments))
            printf_format = f"    printf(\" - {field_type} ("
            printf_format += ", ".join(values)
            printf_format += "): \");"
            self.append(printf_format)

            # Add print_bytes call
            self.append(f"    print_bytes(&test_{field_type_name}, sizeof(test_{field_type_name}));\n")

        self.append("    return 0;")
        self.append("}")

    # Generate the complete code.
    def generate(self):
        self.generate_includes()
        self.generate_structs()
        self.generate_print_bytes()
        self.generate_main()
        return self.get_result()

def generate():
    return BitFieldGenerator().generate()

if __name__ == "__main__":
    content = generate()
    print(content)
