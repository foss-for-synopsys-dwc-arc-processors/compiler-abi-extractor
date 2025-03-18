#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.


class DumpInformation:
    def __init__(self):
        self.stack_ptr = ""
        self.stack_ptr_size = 0
        self.reg_bank_count = 0
        self.reg_bank_infos = {}
        self.RegBanks = {}
        self.Stack = []

    def get_reg_bank_count(self):
        return self.reg_bank_count

    def get_reg_bank_infos(self):
        return self.reg_bank_infos

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

        # FIXME Use "take while" if it exists.
        header_lines = []
        while content:
            Content = content[0]
            if "//" in Content:
                break

            Content = content.pop(0)
            header_lines.append(Content)

        assert len(header_lines) >= 6

        # header structure:
        #   - stack_ptr : hex
        #   - sizeof(stack_ptr) : hex
        #   - nr_of_register_banks : hex
        # foreach register bank
        #   - bank_id : string
        #   - size of register : hex
        #   - number of registers : hex
        self.stack_ptr = int(header_lines[0], 16)
        self.stack_ptr_size = int(header_lines[1], 16)
        self.reg_bank_count = int(header_lines[2], 16)
        for i in [(x * 3) + 3 for x in range(self.reg_bank_count)]:
            bank_id = header_lines[i]
            reg_bank_info = {}
            reg_bank_info["size"] = int(header_lines[i + 1], 16)
            reg_bank_info["nr"] = int(header_lines[i + 2], 16)
            self.reg_bank_infos[bank_id] = reg_bank_info

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


def get_reg_banks():
    return DumpInformation().get_reg_banks()


def get_stack(self):
    return DumpInformation().get_stack()


def split_dump_sections(Content):
    return DumpInformation().split_dump_sections(Content)


def parse(Content, to_read=False):
    return DumpInformation().parse(Content, to_read)
