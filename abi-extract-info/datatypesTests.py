#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

Types = [ "char", "signed char", "unsigned char", "short", "int", "long", "long long",
          "float", "double", "long double",
        ]

class DataTypesGenerator:
    def __init__(self):
        self.Result = []
        self.Globals = []

    def append(self, W):
        self.Result.append(W)
        
    def generateBase(self):
        self.append("""
#include <stdio.h>
#include <stdint.h>

void print_info(const char *datatype, size_t size, uintptr_t theOffset) {
   printf("%-20s: size: %zu, align: %zu\\n", datatype, size, (size_t)theOffset);
}

""")

    # Generate global variabels for each type and print runtime information about them
    def generateTypeChecksUsingGlobals(self):
        for I, T in enumerate(Types):
            # Ensure we always start with an odd address (as far as C standard guarantees this)
            self.append(f"char dummy{I};")
            self.append(f"{T} type{I};\n")

        self.append("void analyzeTypesUsingGlobals() {")
        for I, T in enumerate(Types):
            self.append(f"  print_info(\"{T}\", sizeof({T}), (uintptr_t)&type{I}-(uintptr_t)&dummy{I});")
        self.append("}\n")

    def generateMain(self):
        self.append("""
int main() {
  analyzeTypesUsingGlobals();
}
""")

    def getResult(self):
        return "\n".join(self.Result)

    def generate(self):
        self.generateBase()
        self.generateTypeChecksUsingGlobals()
        self.generateMain()

        return self.getResult()
    
def generate():
    return DataTypesGenerator().generate()
