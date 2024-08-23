#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This class is responsible for generating the summary report
and the proper calls to validate each dump information.
"""

from lib import hexUtils
from lib import helper

class SavedTests:
    def __init__(self, Target):
        self.Target = Target

    def generate_summary(self, callee, caller):
        summary = []
        summary.append("caller/callee-saved:")
        summary.append(f" - caller-saved {caller}")
        summary.append(f" - callee-saved {callee}")

        return "\n".join(summary)

    def run_test(self, register_banks, sizeof):
        hutils = hexUtils.HexUtils(self.Target)

        caller_saved_argv = helper.generate_hexa_values_2(sizeof, 30)
        caller_saved_registers = hutils.find_registers_fill([caller_saved_argv], register_banks)

        callee_saved_argv = helper.generate_hexa_values_2(sizeof)
        callee_saved_registers = hutils.find_registers_fill([callee_saved_argv], register_banks)


        return self.generate_summary(caller_saved_registers, callee_saved_registers)