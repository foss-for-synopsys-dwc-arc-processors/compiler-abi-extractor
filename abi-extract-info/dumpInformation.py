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

    def get_header_info(self, index):
        return self.HeaderInfo[index]

    def get_reg_banks(self):
        return self.RegBanks

    def get_stack(self):
        return self.Stack

    def read_file(self, file_name):
        with open(file_name, "r") as file:
            return file.read().splitlines()

    # Read Header from the "dump_information" provided by "src/helper.c"
    def read_header(self, content):
        if "// Header info" not in content[0]:
            #            return content
            return self.read_header(content[1:])

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

        # Pop comment - "// regs_bank"
        reg_bank = content.pop(0)
        # Delete `// `
        reg_bank = reg_bank[3:]
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

    # Read Stack dump from "dump_information" provided by "src/helper.c"
    def read_stack(self, content):
        if "// Start of stack dump" not in content[0]:
            return content

        # This is currently being discarded, should it?. FIXME
        content.pop(0)

        while content:
            Content = content[0]
            if "//" in Content:
                break

            Content = content.pop(0)
            Content = Content.split(" : ")

            self.Stack.append(Content)

        return Content

    # Split dump information from multiple dumps within a single C file.
    # This occurs when there are multiple calls to the extern callee()
    # function in a test case.
    def split_dump_sections(self, StdoutFile):
        Content = self.read_file(StdoutFile)
        result = []
        current_sublist = []

        for c in Content:
            if "// Done" in c:
                result.append(current_sublist)
                current_sublist = []
            else:
                current_sublist.append(c)

        return result

    def parse_lines(self, lines):
        lines = self.read_header(lines)
        lines = self.read_reg_banks(lines)
        lines = self.read_stack(lines)

        return lines

    def parse(self, Content):
        return self.parse_lines(Content.splitlines())


def get_header_info(index):
    return DumpInformation().get_header_info(index)


def get_reg_banks():
    return DumpInformation().get_reg_banks()


def get_stack(self):
    return DumpInformation().get_stack()


def split_dump_sections(Content):
    return DumpInformation().split_dump_sections(Content)


def parse(Content, to_read=False):
    return DumpInformation().parse(Content, to_read)
