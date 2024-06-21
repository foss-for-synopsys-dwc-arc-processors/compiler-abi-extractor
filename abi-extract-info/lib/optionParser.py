#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import sys
import os

class OptionParser:
    _instance = None

    def __init__(self):
        self.flags = {}

    @classmethod
    def instance(cls):
        cls._instance = cls._instance or cls()
        return cls._instance

    def set(self, name, default_value=True):
        self.flags[name] = default_value

    def get(self, name):
        return self.flags.get(name, False)

    def helper(self):
        return

    def set_default(self):
        self.set("verbose", False)

    def option_parser(self, args = sys.argv):
        self.set_default()
        args.pop(0)
        while args:
            arg = args.pop(0)
            if arg == "-h" or arg == "--help":
                self.help()
            elif arg == "-cc" or arg == "--compiler":
                compiler = args.pop(0)
                self.set("cc", compiler)
            elif arg == "-sim" or arg == "--simulator":
                simulator = args.pop(0)
                self.set("sim", simulator)
            elif arg == "-v" or arg == "--verbose":
                self.set("verbose")
            elif arg == "--print-report":
                self.set("print-report")
