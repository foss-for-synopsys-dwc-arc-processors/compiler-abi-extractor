# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import dumpInformation

"""
The purpose of this generator is to create a test case
that will validate if empty structs are ignored by the C
compiler as stated in RISCV ABI document.

RISC-V ABIs Specification v1.1
* Chapter 2. Procedure Calling Convention
** 2.1. Integer Calling Convention
***  "Empty structs (...) are ignored by C compilers (...)"
"""
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

"""
The logic relies on validating the presence of the keyword ("0xdead") in the
argument passing registers for a given architecture to ensure that an empty
struct is ignored by the C compiler.

Here's how it works:
We will pass the empty struct as an argument alongside a sentinel value
denoting the boundaries. Then test the empty struct in all possible positions
in the argument list, for example:

callee (S, I)
callee (I, S, I)
callee (I, I, S, I)
...

where:
    "S" represents the empty struct
    "I" represents the sentinel value.

For each information dump (each "callee" call), it is verified that only the
value of "I" ("0xdead") is present in the argument passing registers. This
confirms that the empty struct is indeed being ignored by the C compiler.
"""
class EmptyStructValidator:
    def __init__(self, Target):
        self.Result = list()
        self.Mapping = dict()
        self.Target = Target
        self.Keyword = "0xdead"

    def validate_if_ignored(self, bank_name, regs_bank, count):
        target = self.Target
        for i, r in enumerate(target.get_registers(bank_name)):
            self.Mapping[r] = regs_bank[i]

        is_ignored = False
        for i in range(count):
            a = target.get_argument_registers()[i]
            if self.Mapping[a] == self.Keyword:
                is_ignored = True
            else:
                is_ignored = False
                break

        return is_ignored

    # This function needs to be moved to a "lib/helper" as a module
    # to be access globaly. FIXME
    def read_file(self, file_name):
        with open(file_name, "r") as file:
            return file.read().splitlines()

    # This function should be in the "dumpInformation" class. FIXME
    def split_sections(self, StdoutFile):
        Content = self.read_file(StdoutFile)

        result = []
        current_sublist = []

        for c in Content:
            if "// Done" in c:
                result.append(current_sublist)
                current_sublist = []
            else:
                current_sublist.append(c)

        dump_information = dumpInformation.DumpInformation()
        for count, sublist in enumerate(result):
            dump_information.parse(sublist)

            for key, value in dump_information.RegBanks.items():
                is_ignored = self.validate_if_ignored(key, value, count + 1)
                if is_ignored is False:
                    break

        if is_ignored:
            return "- empty struct is ignored by C compiler.\n"
        else:
            return "- empty struct is not ignored by C compiler.\n"

def do_empty_struct(Driver, Report, Target):
    # This value is to be defined according to number for
    # argument passing in registers from "do_argpass" test case.
    MaxCallCount = 8 # Current static value. FIXME
    Content = EmptyStructGenerator(MaxCallCount).generate()
    open("tmp/out_emptyStruct.c", "w").write(Content)

    source_files   = ["tmp/out_emptyStruct.c", "src/helper.c"]
    assembly_files = ["src/arch/riscv.S"]
    output_name = "out_emptyStruct"
    res, StdoutFile = Driver.run(source_files, assembly_files, output_name)
    if res != 0:
        print("Skip: Empty Struct test case failed.")
        return

    content = EmptyStructValidator(Target).split_sections(StdoutFile)
    return content
