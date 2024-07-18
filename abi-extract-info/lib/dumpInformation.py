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

def parse(Content, to_read = False):
    dump = DumpInformation()
    if to_read:
        Content = dump.read_file(Content)

    return Content
