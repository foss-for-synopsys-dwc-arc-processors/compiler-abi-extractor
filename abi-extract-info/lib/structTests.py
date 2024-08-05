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

    def remove_none_from_nested_list(self, list_of_regs):
        return [item for item in list_of_regs if item is not None]

    # Extracts the common registers in a list of list registers.
    def extract_common_regs(self, list_of_regs):
        list_of_regs = self.remove_none_from_nested_list(list_of_regs)
        if list_of_regs == []:
            return None, None

        # Convert each sublist to a set
        sets = [set(lst) for lst in list_of_regs]

        # Find common elements by intersecting all sets
        common_elements = set.intersection(*sets)

        # Find all unique elements by taking the union of all sets
        all_elements = set.union(*sets)

        # Find non-common elements by subtracting common elements from all unique elements
        non_common_elements = all_elements - common_elements

        ordered_common = []
        ordered_non_common = []

        # Preserving the order from the original lists
        for lst in list_of_regs:
            for elem in lst:
                if elem in common_elements and elem not in ordered_common:
                    ordered_common.append(elem)
                elif elem in non_common_elements and elem not in ordered_non_common:
                    ordered_non_common.append(elem)

        return ordered_common, ordered_non_common

    # Generate a summary string from the extracted information.
    def create_summary_string(self, results):
        summary = []

        for argument_count, value in results.items():
            # Join the types into a single string separated by ' : '
            types = " : ".join(value["type"])

            description = ""

            # Check if values are passed in registers and not on stack
            if value["common_regs"] and not value["are_values_on_stack"]:
                common_regs = " ".join(value["common_regs"])
                description = f"passed in registers: {common_regs}"

            # Check if values are passed on stack and not in registers
            elif not value["common_regs"] and value["are_values_on_stack"]:
                description = f"passed in stack: sp ..."

            # Check if values are split and passed in registers
            elif value["common_regs"] and value["are_values_splitted"] and not value["are_values_on_stack"]:
                common_regs = " ".join(value["common_regs"])
                values_splitted = ", ".join(value["are_values_splitted"])
                description = f"passed in registers {values_splitted}: {common_regs}"

            # Check if values are split and passed on stack
            elif not value["common_regs"] and value["are_values_splitted"] and value["are_values_on_stack"]:
                values_splitted = ", ".join(value["are_values_splitted"])
                description = f"passed in stack {values_splitted}: sp ..."

            # Check if values are passed in both registers and stack
            elif value["common_regs"] and value["are_values_on_stack"] and not value["are_values_splitted"]:
                common_regs = " ".join(value["common_regs"])
                description = f"passed in registers/stack: {common_regs} sp ..."

            # Check if values are split and passed in both registers and stack
            elif value["common_regs"] and value["are_values_on_stack"] and value["are_values_splitted"]:
                common_regs = " ".join(value["common_regs"])
                values_splitted = ", ".join(value["are_values_splitted"])
                description = f"passed in registers/stack {values_splitted}: {common_regs} sp ..."

            # Build the summary string for each argument
            summary.append(f"- {types}\n")
            summary.append(f" - argc > {argument_count} : {description}\n")

            # Add a warning message if there are non-common registers
            if value["noncommon_regs"]:
                summary.append(" - WARNING: some inconsistencies were detected, for details see ......\n")

        return "".join(summary)

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
