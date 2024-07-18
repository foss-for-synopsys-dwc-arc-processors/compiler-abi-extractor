#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

class DumpInformation:
    def __init__(self):
        self.HeaderInfo = list()
        self.RegBanks = dict()
        self.Stack = list()

    def read_file(self, file_name):
        with open(file_name, "r") as file:
            return file.read().splitlines()

    # Read Header from the "dump_information" provided by "src/helper.c"
    def read_header(self, content):
        if "// Header info" not in content[0]:
            return content

        # Delete comment - "// Header info"
        content.pop(0)

        while content:
            Content = content[0]
            if "//" in Content:
                break

            Content = content.pop(0)
            self.HeaderInfo.append(Content)

        return content

    # Read Register Banks from the "dump_information" provided by "src/helper.c"
    def read_reg_banks(self, content):
        if "// regs_bank" not in content[0]:
            return content

        # Delete comment - "// regs_bank"
        reg_bank = content.pop(0)
        self.RegBanks[reg_bank] = list()

        while content:
            Content = content[0]
            if "//" in Content:
                if "// regs_bank" in Content:
                    self.read_reg_banks(content)
                    break
                else:
                    break

            Content = content.pop(0)
            self.RegBanks[reg_bank].append(Content)

        return content

def parse(Content, to_read = False):
    dump = DumpInformation()
    if to_read:
        Content = dump.read_file(Content)

    return Content
