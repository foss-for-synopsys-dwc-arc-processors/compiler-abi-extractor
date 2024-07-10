#! /bin/env python
"""
The purpose of this script is to produce a range of
C test cases utilizing various structs using
fundamental C types for the callee function.

The output will comprise a list detailing the datatypes
alongside their respective C test cases.
"""

# Class to generate C code files with functions
# taking multiple arguments of different types
class ArgPassGenerator:
    def __init__(self):
        # List to store the generated code for the current file
        self.Result = []
        # Dictionary mapping data types to hexadecimal values
        self.type_value_generator = {
            "char": [0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D,
                     0x4E, 0x4F, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55],
            "int": [0x3e9, 0x3ea, 0x3eb, 0x3ec, 0x3ed, 0x3ee, 0x3ef, 0x3f0,
                    0x3f1, 0x3f2, 0x3f3, 0x3f4, 0x3f5, 0x3f6, 0x3f7, 0x3f8],
            "double": [0x3fe2788cfc6f802a, 0x3fe62e42fef1fccc, 0x3fe921fb544486e0,
                       0x3ff33ba004f2ccf4, 0x3ff6a09e667a35e6, 0x3ff71547652565ef,
                       0x3ff921fb6f1c797b, 0x3ff9e3779b9486e5, 0x3ffbb67ae85390f7,
                       0x4001e3779b97f681, 0x40026bb1bbb219d9, 0x400405f4906034f4,
                       0x40052a7fa9d43061, 0x4005bf0a8b12500b, 0x400921fb54411744,
                       0x40094c583ad801da],
        }

    def append(self, W):
        self.Result.append(W)

    def reset(self):
        self.Result = []

    def generateHeader(self):
        self.append("#include <string.h>")

    def generateStruct(self, datatype, content):
        length = len(content)
        self.append(f"struct {datatype}Struct " + "{")
        for I in range(length):
            self.append(f"{datatype} type{I};")
        self.append("};")

    def generateConverter(self):
        self.append(f"inline static double ull_as_double(unsigned long long lhs)")
        self.append("{")
        self.append(f"double result;")
        self.append(f"memcpy(&result, &lhs, sizeof(result));")
        self.append("return result;")
        self.append("}")

    # Generate the base structure of the C file,
    # including the function prototype and main function
    def generateBase(self, type_name, content):
        # Convert each hexadecimal value to a formatted string and join them with ","
        values = ",".join(f"ull_as_double(0x{hex(value)[2:].upper()})" for value in content)
        self.append(f"extern void callee(struct {type_name}Struct types);")
        self.append("int main(void) {")
        self.append(f"struct {type_name}Struct types = {{{values}}};")
        self.append(f"callee(types);")
        self.append("}")

    def getResult(self):
        return "\n".join(self.Result)

    # Generate a single C file with the specified types
    def generateFile(self, type_name, content):
        # Reset the result list
        self.reset()

        self.generateHeader()
        self.generateConverter()
        self.generateStruct(type_name, content)

        # Generate the base structure
        self.generateBase(type_name, content)

        return self.getResult()

    # Generate multiple C files,
    # one for each type in the type_value_generator dictionary
    def generate(self):
        files = []

        for type_name, content in self.type_value_generator.items():
            files.append((type_name, self.generateFile(type_name, content)))
        return files

# Function to initiate the generation process
def generate():
    return ArgPassGenerator().generate()

import sys
if __name__ == "__main__":
    # Generating the files content
    files_content = generate()

    # Writing the generated files content to separate files
    for type_name, content in files_content:
        with open(f"tmp/caller_{type_name}.c", "w") as file:
            file.write(content)

