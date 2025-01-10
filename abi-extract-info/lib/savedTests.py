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

class SavedTests:
    def __init__(self, Target):
        self.Target = Target

    def generate_summary(self, caller, callee):

        caller_str = ", ".join(caller)
        callee_str = ", ".join(callee)

        summary = []
        summary.append("Caller/callee-saved test:")
        summary.append(f" - caller-saved {caller_str}")
        summary.append(f" - callee-saved {callee_str}")
        summary.append("")

        return "\n".join(summary)

    def run_test(self, register_banks, hvalue_caller_saved, hvalue_callee_saved):
        hutils = hexUtils.HexUtils(self.Target)

        tmp = hutils.find_registers_fill([hvalue_caller_saved], register_banks)
        caller_saved_registers, _  = tmp

        tmp = hutils.find_registers_fill([hvalue_callee_saved], register_banks)
        callee_saved_registers, _ = tmp

        return self.generate_summary(caller_saved_registers, callee_saved_registers)