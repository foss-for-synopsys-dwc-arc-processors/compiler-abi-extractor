#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
The purpose of this generator is to create a test case
that will validate if empty structs are ignored by the C
compiler as stated in RISCV ABI document.

RISC-V ABIs Specification v1.1
* Chapter 2. Procedure Calling Convention
** 2.1. Integer Calling Convention
***  "Empty structs (...) are ignored by C compilers (...)"
"""

import sys

class EmptyStructGenerator:
    def __init__(self, MaxCallCount):
        self.Result = []
        # CallCount is the max number for argument passing in registers,
        # plus 1 because we also want to validate the empty struct at the
        # last argument passing register.
        self.MaxCallCount = MaxCallCount + 1

        # Default to 2 as there gotta be place for the struct and a sentinel
        # defining the end limits of the argument passing.
        self.CallCount = 2

    def append(self, W):
        self.Result.append(W)

    def generateBase(self):
        self.append("""
struct emptyStruct {
};

extern void callee();
""")

    def generateCalls(self):
        call_arguments = []
        I = "I"
        S = "S"

        for i in range(self.CallCount):
            if i == self.CallCount - 2:
                call_arguments.append(S)
            else:
                call_arguments.append(I)

        self.append(f"    callee({', '.join(call_arguments)});")

        # Increment the call count for the next generation.
        self.CallCount += 1

    def generateMain(self):
        call_arguments = []


        self.append("""
int main (void) {
    int I = 0xdead;
    struct emptyStruct S;
""")

        for i in range(self.CallCount, self.MaxCallCount + 1):
            self.generateCalls()

        self.append("}")

    def Reset(self):
        self.Result = []

    def getResult(self):
        return "\n".join(self.Result)

    def generate(self):
        self.generateBase()
        self.generateMain()

        result = self.getResult()
        self.Reset()
        return result

def generate(MaxCallCount):
    # MaxCallCount is the max number for argument passing in registers.
    return EmptyStructGenerator(MaxCallCount).generate()

import sys
if __name__ == "__main__":
    # Testing purposes.
    #   The expected number of argument passing registers from RISCV ABI
    #   is 8.
    MaxCallCount = 8
    Content = generate(MaxCallCount)
    print(Content)
