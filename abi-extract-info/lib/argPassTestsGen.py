#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
The purpose of this script is to produce a range of
C test cases utilizing various fundamental C types
for the callee function.

The output will comprise a list detailing the datatypes
alongside their respective C test cases.

TODO: Expand the range of supported data types.
"""

# Class to generate C code files with functions
# taking multiple arguments of different types
class ArgPassGenerator:
    def __init__(self):
        # List to store the generated code for the current file
        self.Result = []
        # Dictionary mapping data types to lambda functions that generate appropriate values
        self.type_value_generator = {
            "char": [f"'{chr(70 + i)}'" for i in range(16)],
            "signed char": [-i - 21 for i in range(16)],
        }

    def append(self, W):
        self.Result.append(W)

    def reset(self):
        self.Result = []

    # Generate the base structure of the C file,
    # including the function prototype and main function
    def generateBase(self, types):
        prototype_params = ", ".join(types)
        # Generate corresponding values for the types using the type_value_generator dictionary
        call_params = ", ".join(str(val) for val in self.type_value_generator[types[0]])

        self.append(f"""
extern void callee({prototype_params});

int main(void) {{
    callee({call_params});
}}
""")

    def getResult(self):
        return "\n".join(self.Result)

    # Generate a single C file with the specified types
    def generateFile(self, types):
        # Reset the result list
        self.reset()
        # Generate the base structure
        self.generateBase(types)

        return self.getResult()

    # Generate multiple C files,
    # one for each type in the type_value_generator dictionary
    def generate(self):
        files = []
        for type_name, content in self.type_value_generator.items():
            # Create a list of identical types
            types = [type_name for _ in range(len(content))]
            # Generate the file and store the result
            files.append((type_name, self.generateFile(types)))
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
        with open(f"caller_{type_name}.c", "w") as file:
            file.write(content)

