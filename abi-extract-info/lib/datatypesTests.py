#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

Types = [ "char", "signed char", "unsigned char", "short", "int", "long", "long long",
          "void*", "float", "double", "long double",
        ]

Structs = ["char_short_int", "char_short_double"]

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

void print_info(const char *datatype, int signedness, size_t size, uintptr_t theOffset) {
   printf("%-20s: signedness: %d, size: %zu, align: %zu\\n", datatype, signedness, size, (size_t)theOffset);
}

""")

    # Generate global variabels for each type and print runtime information about them
    def generateTypeChecksUsingStructs(self):
        for I, S in enumerate(Structs):
            # Generate Struct definition for the struct argument passing
            arr = S.split("_")
            self.append("struct " + S + " {")
            for index, datatype in enumerate(arr):
                self.append(f"{datatype} theType{index};")
            self.append("};")

            self.append("""struct StructType%d {
char dummy;
struct %s theType;
} theStructTypeObject%d;
""" % (I, S, I))

        for I, T in enumerate(Types):
            # Ensure we always start with an odd address (as far as C standard guarantees this)
            self.append("""struct Type%d {
  char dummy;
  %s theType;
} theTypeObject%d;
""" % (I, T, I))

        self.append("void analyzeTypesUsingGlobals() {")
        for I, T in enumerate(Types):
            # Omitting the assignment of "-1" to "void*" because some compilers consider it an error.
            if T != "void*":
                self.append(f"  theTypeObject{I}.theType = -1;")
                self.append(f"  print_info(\"{T}\", theTypeObject{I}.theType == -1, sizeof({T}), (uintptr_t)&theTypeObject{I}.theType-(uintptr_t)&theTypeObject{I}.dummy);")
            else:
                self.append(f"  print_info(\"{T}\", 0, sizeof({T}), (uintptr_t)&theTypeObject{I}.theType-(uintptr_t)&theTypeObject{I}.dummy);")

        for I, T in enumerate(Structs):
            self.append(f"  print_info(\"{T}\", 0, sizeof(struct {T}), (uintptr_t)&theStructTypeObject{I}.theType-(uintptr_t)&theStructTypeObject{I}.dummy);")

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
        self.generateTypeChecksUsingStructs()
        self.generateMain()

        return self.getResult()
    
def generate():
    return DataTypesGenerator().generate()
