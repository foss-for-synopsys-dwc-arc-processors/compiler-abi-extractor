#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
The purpose of this class is to validate the presence of a value in the stack.
In the argument passing test case, we aim to understand how the compiler
behaves with different argument counts.

Key questions include:
 - Are registers used for argument passing?
 - Are values passed directly on the stack?
 - Is a stack pointer reference passed in a register?

We also examine how argument count varies with datatype size.

For example, in a 32-bit architecure with 8 argument passing registers:
- For a 4-byte datatype (32-bit), it is expected that all 8 values can be
passed using the registers.
- For an 8-byte datatype (64-bit), only 4 values can be passed using the
registers, as each 8-byte value will occupy two registers.
"""

from lib import helper
from lib import hexUtils

class ArgPassTests:
    def __init__(self, Target):
        self.Target = Target
        self.results = []

    # Extracts the common registers in a list of list registers.
    def extract_common_regs(self, list_of_regs):
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
        summary = ["Passing arguments test:"]

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
                description = f"passed in stack: [stack] ..."

            # Check if values are split and passed in registers
            elif value["common_regs"] and value["are_values_splitted"] and not value["are_values_on_stack"]:
                common_regs = " ".join(value["common_regs"])
                values_splitted = ", ".join(value["are_values_splitted"])
                description = f"passed in registers {values_splitted}: {common_regs}"

            # Check if values are split and passed on stack
            elif not value["common_regs"] and value["are_values_splitted"] and value["are_values_on_stack"]:
                values_splitted = ", ".join(value["are_values_splitted"])
                description = f"passed in stack {values_splitted}: [stack] ..."

            # Check if values are passed in both registers and stack
            elif value["common_regs"] and value["are_values_on_stack"] and not value["are_values_splitted"]:
                common_regs = " ".join(value["common_regs"])
                description = f"passed in registers/stack: {common_regs} [stack] ..."

            # Check if values are split and passed in both registers and stack
            elif value["common_regs"] and value["are_values_on_stack"] and value["are_values_splitted"]:
                common_regs = " ".join(value["common_regs"])
                values_splitted = value["are_values_splitted"]
                description = f"passed in registers/stack {values_splitted}: {common_regs} [stack] ..."

            # Build the summary string for each argument
            summary.append(f"- {types}")
            summary.append(f" - argc > {argument_count} : {description}")

            # Add a warning message if inconsistencies are found.
            if value["inconsistencies"]:
                # Convert an list of string tuples to a single string.
                # e.g [("reg1", "reg2"), ("reg3", "reg4")]:
                # - WARNING: multiple value occurrences detected in (reg1, reg2), (reg3, reg4)
                inconsistencies = ", ".join(f"({', '.join(i)})" for i in value["inconsistencies"])
                summary.append(f" - WARNING: multiple value occurrences detected in {inconsistencies}")

            # Add a warning message if there are non-common registers
            if value["noncommon_regs"]:
                summary.append(" - WARNING: some inconsistencies were detected, for details see ......")

        summary.append("")
        return "\n".join(summary)

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Argument count value
        argc = len(argv)

        # Initialize current test details
        citeration = {
            "argc": argc,               # Argument count
            "argv": argv,               # Value checked
            "value_split_order": None,  # Order of split values (if any)
            "registers": None,          # Registers containing the value
            "value_in_stack": None      # Wether the value is in the stack
        }

        # Check if the value is in the registers and update current test
        tmp = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers"], citeration["inconsistencies"] = tmp
        if not citeration["registers"]:
            tmp = hutils.find_registers_pairs(argv.copy(), register_banks)
            citeration["registers"], citeration["inconsistencies"], citeration["pairs_order"] = tmp

        # Check if the value is in the stack and update current test
        tmp = hutils.find_value_fill_in_stack(citeration, argv.copy(), stack)
        citeration["value_in_stack"], citeration["inconsistencies"] = tmp
        if not citeration["value_in_stack"]:
            tmp = hutils.find_value_pairs_in_stack(citeration, argv.copy(), stack)
            citeration["value_in_stack"], citeration["inconsistencies"] = tmp

        return citeration

import sys
if __name__ == "__main__":
    pass
