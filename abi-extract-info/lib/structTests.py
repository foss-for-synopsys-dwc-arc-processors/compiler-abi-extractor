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

from lib import hexUtils

class StructTests:
    def __init__(self, Target):
        self.Target = Target
        self.results = []

    # Process the results to categorize them according to their registers
    # and if values were splitted in pairs.
    def process_results(self, results):
        types = []
        passed_by_ref = {}
        boundary = {}

        # Get the size of a registers.
        register_size = self.Target.get_type_details("int")["size"]
        for dtype, iterations in results.items():
            if len(iterations) > 1:
                iteration = iterations[-2]

                # Get the size of the current datatype
                sizeof_dtype = self.Target.get_type_details(dtype)["size"]

                if not types:
                    if sizeof_dtype == register_size:
                        types.append({ "dtypes": [dtype], "regs": list(iteration["registers_fill"].keys()), "pairs": ""})
                    elif sizeof_dtype < register_size:
                        types.append({ "dtypes": [dtype], "regs": list(iteration["registers_combined"].keys()), "pairs": ""})
                    elif sizeof_dtype > register_size:
                        types.append({ "dtypes": [dtype], "regs": list(iteration["registers_pairs"].keys()), "pairs": iteration["pairs_order"]})
                    continue

                # Get the registers according to the size type.
                if sizeof_dtype == register_size:
                    regs = list(iteration["registers_fill"].keys())
                elif sizeof_dtype < register_size:
                    regs = list(iteration["registers_combined"].keys())
                elif sizeof_dtype > register_size:
                    regs = list(iteration["registers_pairs"].keys())
                pairs = iteration["pairs_order"]

                found = False
                for x in types.copy():
                    # Aggregate the dtype according to their registers
                    # used and if they are in pairs.
                    if regs == x["regs"] and pairs == x["pairs"]:
                        x["dtypes"].append(dtype)
                        found = True
                        break

                if not found:
                    types.append({ "dtypes": [dtype], "regs": regs, "pairs": pairs })

            # Track the boundary values based on the sizeof(S) for the second last iteration.
            if len(iterations) >= 2:
                boundary[iterations[-2]["sizeof(S)"]] = ""
                passed_by_ref[iterations[-1]["passed_by_ref"]] = ""

        # Get the voundary value and the pass-by-ref value.
        boundary_value = next(iter(boundary.keys()), None)
        passed_by_ref_value = next(iter(passed_by_ref.keys()), None)


        return types, boundary_value, passed_by_ref_value

    # Create a summary
    def summary_results(self, types, boundary_value, passed_by_ref_value):
        summary = [
            "Struct argument passing test:",
            f"- sizeof(S) <= {boundary_value} : passed in registers",
            f"- sizeof(S) >  {boundary_value} : passed by ref: {passed_by_ref_value}"
        ]
        for i in types:
            dtypes_str = ' : '.join(i["dtypes"])
            regs_str   = ', '.join(i["regs"])
            pairs_str  = i["pairs"]
            summary.append(f"  - {dtypes_str} {pairs_str}: {regs_str}")

        summary.append("")
        return summary

    # Prepare the summary based on the test case results.
    def prepare_summary(self, results):
        # process the results
        types, boundary_value, passed_by_ref_value = self.process_results(results)

        # Summarize and output the results
        summary = self.summary_results(types, boundary_value, passed_by_ref_value)
        return "\n".join(summary)

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, citeration, dtype, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Get sizeof() of current iteration's struct.
        sizeofs = [hutils.sizeof(value) for value in argv]
        citeration["sizeof(S)"] = sum(sizeofs)

        # Check if the value is in the registers and update current test
        tmp = hutils.find_ref_in_stack_fill(dtype, argv.copy(), register_banks, stack)
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration

        tmp = hutils.find_ref_in_stack_pairs(dtype, argv.copy(), register_banks, stack)
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration

        tmp = hutils.find_ref_in_stack_combined(dtype, argv.copy(), register_banks, stack)
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration


        tmp = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers_fill"], _ = tmp

        tmp = hutils.find_registers_pairs(argv.copy(), register_banks)
        citeration["registers_pairs"], _, citeration["pairs_order"] = tmp

        tmp = hutils.find_registers_combined(argv.copy(), register_banks)
        citeration["registers_combined"], _ = tmp

        return citeration


if __name__ == "__main__":
    pass
