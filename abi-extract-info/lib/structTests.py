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
        self.results = []

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

    # Populate the "fill" type register entries for a given data type.
    def handle_registers_fill(self, iteration, dtype, types, passed_by_ref):
        for reg in iteration.get("registers_fill", []):
            types["fill"].setdefault(reg, []).append(dtype)
        # If the iteration is marked as passed by reference, store it.
        if iteration.get("passed_by_ref"):
            passed_by_ref[iteration["passed_by_ref"]] = ""

    # Polupate the "combined" type register entries for a given data type.
    def handle_registers_combined(self, iteration, dtype, types):
        for reg in iteration.get("registers_combined", []):
            types["combined"].setdefault(reg, []).append(dtype)

    # Polupate the "pairs" type register entries for a given data type.
    def handle_registers_pairs(self, iteration, dtype, types):
        for reg in iteration.get("registers_pairs", []):
            types["pairs"].setdefault(reg, []).append(dtype)

    # Process the results to categorize data types based on how
    # they are passed (in registers or by reference), and determines boundary values.
    def process_results(self, results):
        types = { "fill": {}, "combined": {}, "pairs": {}}
        passed_by_ref = {}
        boundary = {}

        # Determine the register size.
        register_size = self.Target.get_type_details("int")["size"]
        for dtype, iterations in results.items():
            for iteration in iterations:
                sizeof_s = iteration["sizeof(S)"]

                # Get the size of the current data type.
                sizeof_dtype = self.Target.get_type_details(dtype)["size"]

                # Categorize based on the size comparison with register sizeof.
                if sizeof_dtype == register_size:
                    self.handle_registers_fill(iteration, dtype, types, passed_by_ref)
                elif sizeof_dtype < register_size:
                    self.handle_registers_combined(iteration, dtype, types)
                elif sizeof_dtype > register_size:
                    self.handle_registers_pairs(iteration, dtype, types)

            # Track the boundary vakyes based on the sizeof(S) for the second last iteration.
            if len(iterations) >= 2:
                boundary[iterations[-2]["sizeof(S)"]] = ""

        # Get the voundary value and the pass-by-ref value.
        boundary_value = next(iter(boundary.keys()), None)
        passed_by_ref_value = next(iter(passed_by_ref.keys()), None)

        return types, boundary_value, passed_by_ref_value

    # Create a summary of how different data types structs are passed,
    # categorizing them as "fill", "combined", "pairs".
    def summary_results(self, types, boundary_value, passed_by_ref_value):
        # Collect all unique registers.
        registers = list(set(types["fill"]) | set(types["combined"]) | set(types["pairs"]))
        summary = [
            "struct pasing:",
            f"- sizeof(S) <= {boundary_value} : passed in registers: {', '.join(map(str, registers))}",
            f"- sizeof(S) >  {boundary_value} : passed by ref: {passed_by_ref_value}"
        ]

        # Organize the data types under each category.
        dtypes = {
            key: list({dtype for values in dtype_list.values() for dtype in values})
            for key, dtype_list in types.items()
        }

        # Append the categorized data types to the summary.
        summary.extend([
            f"  - {', '.join(dtypes['fill'])} : as fill",
            f"  - {', '.join(dtypes['combined'])} : as combined",
            f"  - {', '.join(dtypes['pairs'])} : as pairs"
        ])

        return summary

    # Prepare the summary based on the test case results.
    def prepare_summary(self, results):
        # process the results
        types, boundary_value, passed_by_ref_value = self.process_data(results)

        # Summarize and output the results
        summary = self.summary_results(types, boundary_value, passed_by_ref_value)
        print("\n".join(summary))

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, citeration, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Get sizeof() of current iteration's struct.
        sizeofs = [hutils.sizeof(value) for value in argv]
        citeration["sizeof(S)"] = sum(sizeofs)

        # Check if the value is in the registers and update current test
        citeration = hutils.find_ref_in_stack_fill(citeration, argv.copy(), register_banks, stack)
        if citeration["passed_by_ref"]:
            print(citeration)
            return citeration
        citeration = hutils.find_ref_in_stack_pairs(citeration, argv.copy(), register_banks, stack)
        if citeration["passed_by_ref"]:
            print(citeration)
            return citeration
        citeration = hutils.find_ref_in_stack_combined(citeration, argv.copy(), register_banks, stack)
        if citeration["passed_by_ref"]:
            print(citeration)
            return citeration

        citeration["registers_fill"] = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers_pairs"] = hutils.find_registers_pairs(argv.copy(), register_banks)
        citeration["registers_combined"] = hutils.find_registers_combined(argv.copy(), register_banks)

        #print(f"register_banks {register_banks}")
        #print(f"stack {stack}")

        return citeration


if __name__ == "__main__":
    pass
