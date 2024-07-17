#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

Types = [ "char", "signed char", "unsigned char", "short", "int", "long", "long long",
          "void*", "float", "double", "long double",
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

void print_info(const char *datatype, int signedness, size_t size, uintptr_t theOffset) {
   printf("%-20s: signedness: %d, size: %zu, align: %zu\\n", datatype, signedness, size, (size_t)theOffset);
}

""")

    # Generate global variabels for each type and print runtime information about them
    def generateTypeChecksUsingStructs(self):

        # Generate Structs  for each type and print runtime information about them
        for I, T in enumerate(Types):
            self.append("""struct struct_%s {
  char dummy;
  %s theType;
};""" % (T.replace(' ', '_').replace('*', ''), T))

            self.append("""struct StructType%d {
  char dummy;
  struct struct_%s theType;
} theStructTypeObject%d;
""" % (I, T.replace(' ', '_').replace('*', ''), I))

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

        for I, T in enumerate(Types):
            Struct = T.replace(' ', '_').replace('*', '')
            self.append(f"  print_info(\"struct {Struct}\", 0, sizeof(struct struct_{Struct}), (uintptr_t)&theStructTypeObject{I}.theType-(uintptr_t)&theStructTypeObject{I}.dummy);")


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
