#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import helper

"""
The purpose of this generator is to create a test case
that will validate the boundaries before a struct
containing values goes to the stack.

It will generate a test case for a given datatype with
multiple structs being passed to a extern callee() function
responsible for dumping the register and stack values.

These structs are created from 1 to a given MaxCount, where
the last MaxCount will always contain one last "char" element
to validate the boundaries.
"""

import sys

class StructGenerator:
    def __init__(self, MaxCount, Type, values_list):
        self.Result = []
        self.Strings = []
        self.MaxCount = MaxCount
        self.Type = Type
        self.values_list = values_list

    def append(self, W):
        self.Result.append(W)

    def generateDeclarationString(self, count):
        return "".join(f"{self.Type} a{i};\n" for i in range(count))

    def generateDeclarationStringLastChar(self, count):
        return f"char a{count};\n"

    def generateDefinitionString(self, count):
        definition_string = ""

        for i in range(1, count + 1):
            tmp = self.values_list[:i]
            tmp = ", ".join(tmp)
            definition_string += f"    struct structType{i} structTypeObject{i} = {{ {tmp} }};\n"

        tmp = ", ".join(self.values_list)
        definition_string += f"    struct structType{self.MaxCount + 1} structTypeObject{self.MaxCount + 1} = {{ {tmp} }} ;\n"

        return definition_string

    def generateCallString(self, count):
        return "".join(f"    callee(structTypeObject{i});\n" for i in range(1, count + 1 + 1))

    def generateStructDefinitions(self):
        for count in range(1, self.MaxCount + 1):
            declaration_string = self.generateDeclarationString(count)
            self.append("""
struct structType%d {
    %s
};
""" % (count, declaration_string))

        # Always another one with a single char.
        declaration_string = self.generateDeclarationString(self.MaxCount)
        declaration_string += self.generateDeclarationStringLastChar(self.MaxCount)
        self.append("""
struct structType%d {
    %s
};
""" % (self.MaxCount + 1, declaration_string))

    def generateStringInformation(self):
        definition_string = self.generateDefinitionString(self.MaxCount)
        call_string = self.generateCallString(self.MaxCount)

        self.Strings.append(definition_string)
        self.Strings.append(call_string)


    def generateMain(self):
        self.append("extern void callee();")
        self.append("""
int main (void) {
%s
%s
}
""" % (self.Strings[0], self.Strings[1]))

    def Reset(self):
        self.Result = []

    def getResult(self):
        return "\n".join(self.Result)

    def generate(self):
        self.generateStructDefinitions()
        self.generateStringInformation()
        self.generateMain()

        return self.getResult()

def generate(MaxCount, Type, values_list):
    return StructGenerator(MaxCount, Type, values_list).generate()

import sys
if __name__ == "__main__":
    # Testing purposes.
    #  According to RISCV ABI (2x XLEN), if we take into account the int size
    #  from preivous tests, for 32bit we have 2x4=8 and 64bit, 2x8=16
    #  We will hardcore 4bytes for now, but it must be either changed to the
    #  double value of sizeof(int), or a static larger value (e.i 17)
    MaxCount = 2*4
    Type = "int"
    Content = generate(MaxCount, Type, MaxCount)
    print(Content)
