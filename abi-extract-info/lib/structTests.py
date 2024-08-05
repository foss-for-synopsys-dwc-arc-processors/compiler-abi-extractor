#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This class validates how arguments are passed within structs by checking
if a value appears in registers, the stack, or if its passed by reference.
"""

import sys
from lib import hexUtils

class StructTests:
    def __init__(self, Target):
        self.Target = Target

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, stack_address, stack_values, register_banks, values_list):
        # Argument count value
        argc = len(values_list)
        # Target value to be checked
        argv = values_list[0]

        # Initialize current test details
        self.current_test = {
            "argc": argc,               # Argument count
            "argv": argv,               # Value checked
            "value_split_order": None,  # Order of split values (if any)
            "registers": None,          # Registers containing the value
            "value_in_stack": None,     # Wether the value is in the stack
            "passed_by_ref": None       # Wether passed by reference
        }

        hutils = hexUtils.RegisterUtils(self.Target, self.current_test)

        # Check if the value is in the registers and update current test
        self.current_test["registers"] = hutils.find_value_in_registers(argv, register_banks, argc)
        # Check if the value is in the stack and update current test
        self.current_test["value_in_stack"] = hutils.is_value_in_stack(argv, stack_values)
        # Check if the values are being passed by reference and update current test
        self.current_test["passed_by_ref"] = hutils.is_passed_by_ref(stack_address, register_banks)

        # Append current test results to the results list
        self.results.append(self.current_test)

        passed_by_ref = self.current_test["passed_by_ref"]
        self.current_test = {}

        return passed_by_ref


if __name__ == "__main__":
    pass
