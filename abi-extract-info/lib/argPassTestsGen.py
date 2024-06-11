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
            "unsigned char": [i + 21 for i in range(16)],
            "int": [str(-1001 - i) for i in range(16)],
            "unsigned int": [str(1001 + i) for i in range(16)],
            "short": [str(-1001 - i) for i in range(16)],
            "unsigned short": [str(1001 + i) for i in range(16)],
            "long": ["-1142773077", "-1159710506", "-1172818702", "-1175020290",
                     "-1230727382", "-1379698938", "-1407617162", "-1419251393",
                     "-1472002004", "-1472881177", "-1640139052", "-1735560817",
                     "-1802321509", "-1869587600", "-1898404909", "-1914130792"],
            "unsigned long": ["1142773077", "1159710506", "1172818702",
                              "1175020290", "1230727382", "1379698938",
                              "1407617162", "1419251393", "1472002004",
                              "1472881177", "1640139052", "1735560817",
                              "1802321509", "1869587600", "1898404909",
                              "1914130792"],
            "long long": ["-2137669863270891229", "-2522397642985803419",
                          "-3706416192938149415", "-4458567212862610246",
                          "-4953996811516743886", "-5008791413612552904",
                          "-5263960921296054470", "-5659179722960875904",
                          "-6666311942245141952", "-6632755221326625823",
                          "-6912806153521086601", "-7120938963231193120",
                          "-7468639571267450817", "-7939933891726071822",
                          "-8608066631949685570", "-8957140373517805385"],
            "unsigned long long": ["2137669863270891229", "2522397642985803419",
                                   "3706416192938149415", "4458567212862610246",
                                   "4953996811516743886", "5008791413612552904",
                                   "5263960921296054470", "5659179722960875904",
                                   "6666311942245141952", "6632755221326625823",
                                   "6912806153521086601", "7120938963231193120",
                                   "7468639571267450817", "7939933891726071822",
                                   "8608066631949685570", "8957140373517805385"],
            "float": ["0.57f", "0.69f", "0.78f", "1.20f",
                      "1.41f", "1.44f", "1.57f", "1.62f",
                      "1.73f", "2.23f", "2.30f", "2.50f",
                      "2.64f", "2.71f", "3.14f", "3.16f"],
            "double": ["0.5772156649", "0.6931471805", "0.7853981634",
                       "1.2020569032", "1.4142135623", "1.4426950408",
                       "1.5707964268", "1.6180339887", "1.7320508075",
                       "2.2360679775", "2.3025850929", "2.5029078750",
                       "2.6457513111", "2.7182818284", "3.1415926535",
                       "3.1622776601"],
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

