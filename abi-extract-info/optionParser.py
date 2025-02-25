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

    def set_configuration(self, tool, value):
        if not value:
            print(f"fatal: {tool.upper()} configuration not provided.")
            exit(1)
        configurations = self.get_available_configuration(tool)
        if value not in configurations:
            print(f"fatal: {tool.upper()} configuration {value} not found.")
            exit(1)
        self.flags[tool] = value

    def get(self, name):
        return self.flags.get(name, False)

    def get_available_configuration(self, tool):
        tool_path = os.path.join("scripts/wrapper", tool)
        contents = os.listdir(tool_path)
        return contents

    def display_available_configuration(self, tool):
        configurations = self.get_available_configuration(tool)
        print(f"Available configurations for {tool.upper()}:")
        for item in configurations:
            print(f"- {item}")

    def helper(self):
        helper_message = \
"""Usage python3 abi-extract-info [options]
Options:
  -cc <compiler wrapper>        Select the compiler.
  -sim <simulator wrapper>      Select the simulator.
  -v | --verbose                Print execution commands.
  --print-report                Print summary report upon conclusion.
  --save-temps                  Do not delete the temporary files from "tmp/" directory.
  --help                        Display this information.
  --help=cc                     Display available compiler options.
  --help=sim                    Display available simulator options.
"""
        print(helper_message)
        exit(0)

    def set_default(self):
        self.set("cc",  "gcc-rv32gc-ilp32d")
        self.set("sim", "qemu-riscv32")
        self.set("verbose", False)

    def option_parser(self, args = sys.argv[1:]):
            self.set_default()

            actions = {
                "-cc":              lambda: self.set_configuration("cc",  next(arg_iter, None)),
                "--compiler":       lambda: self.set_configuration("cc",  next(arg_iter, None)),
                "-sim":             lambda: self.set_configuration("sim", next(arg_iter, None)),
                "--simulator":      lambda: self.set_configuration("sim", next(arg_iter, None)),
                "-v":               lambda: self.set("verbose"),
                "--verbose":        lambda: self.set("verbose"),
                "--print-report":   lambda: self.set("print-report"),
                "--save-temps":     lambda: self.set("save_temps"),
            }

            help_options = {
                "-h":           self.helper,
                "--help":       self.helper,
                "--help=cc":    lambda: self.display_available_configuration("cc"),
                "--help=sim":   lambda: self.display_available_configuration("sim"),
            }

            to_exit = False
            arg_iter = iter(args)
            for arg in arg_iter:
                if arg in help_options:
                    help_options[arg]()
                    to_exit = True
                elif arg in actions:
                    actions[arg]()
                else:
                    print(f"fatal: Unknown argument: {arg}")
                    exit(1)

            if to_exit:
                exit(0)
