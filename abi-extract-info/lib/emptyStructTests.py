#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

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

import sys
from lib import dumpInformation

class EmptyStructValidator:
    def __init__(self, Target):
        self.Result = list()
        self.Mapping = dict()
        self.Target = Target
        self.Keyword = "0xdead"

    def validate_if_ignored(self, regs_bank, count):
        target = self.Target
        for i, r in enumerate(target.get_registers()):
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
                is_ignored = self.validate_if_ignored(value, count + 1)
                if is_ignored is False:
                    break

        if is_ignored:
            print("    Empty Struct is ignored by C compiler.")
        else:
            print("    Empty Struct is not ignored by C compiler.")

def split_sections(StdoutFile, Target):
    EmptyStructValidator(Target).split_sections(StdoutFile)

if __name__ == "__main__":
    StdoutFile = sys.argv[1]
    EmptyStructValidator().plit_sections(StdoutFile)
    print(Content)