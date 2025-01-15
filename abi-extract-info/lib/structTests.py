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
        boundaries = {}

        for dtype, iterations in results.items():
            # Floating-point registers in RISC-V are 64-bit in size,
            # so we cannot consider the size of an int. If an int is 32-bit,
            # it would split the value, which is incorrect the double data type.
            register_bank_count = self.Target.get_register_bank_count()
            if dtype == "double" and register_bank_count == "0x2":
                register_size = self.Target.get_type_details("double")["size"]
            else:
                register_size = self.Target.get_type_details("int")["size"]

            if len(iterations) > 1:
                iteration = iterations[-2]

                # Get the size of the current datatype
                sizeof_dtype = self.Target.get_type_details(dtype)["size"]

                if not types:
                    if sizeof_dtype == register_size:
                        types.append({ "sizeof(S)": iteration["sizeof(S)"], "dtypes": [dtype], "regs": list(iteration["registers_fill"].keys()), "pairs": ""})
                    elif sizeof_dtype < register_size:
                        types.append({ "sizeof(S)": iteration["sizeof(S)"], "dtypes": [dtype], "regs": list(iteration["registers_combined"].keys()), "pairs": ""})
                    elif sizeof_dtype > register_size:
                        types.append({ "sizeof(S)": iteration["sizeof(S)"], "dtypes": [dtype], "regs": list(iteration["registers_pairs"].keys()), "pairs": iteration["pairs_order"]})
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
                    if regs == x["regs"] and pairs == x["pairs"] and iteration["sizeof(S)"] == x["sizeof(S)"]:
                        x["dtypes"].append(dtype)
                        found = True
                        break

                if not found:
                    types.append({ "sizeof(S)": iteration["sizeof(S)"], "dtypes": [dtype], "regs": regs, "pairs": pairs })

            # Check if there are at least two iterations
            if len(iterations) >= 2:
                second_last_iter = iterations[-2]
                last_iter = iterations[-1]

                # Track the boundary values based on the sizeof(S) for the second last iteration
                sizeof_S = second_last_iter["sizeof(S)"]
                boundaries.setdefault(sizeof_S, []).append(dtype)

                # Record the passed_by_ref status for the last iteration
                passed_by_ref[last_iter["passed_by_ref"]] = ""

        # Get the voundary value and the pass-by-ref value.
        passed_by_ref_value = next(iter(passed_by_ref.keys()), None)

        return types, boundaries, passed_by_ref_value

    # Create a summary
    def summary_results(self, types, boundaries, passed_by_ref_value):
        types_dict = {}
        for type_ in types:
            sizeof = type_["sizeof(S)"]
            types_dict.setdefault(sizeof, []).append(type_)

        summary = ["Struct argument passing test:"]
        for sizeof, types in types_dict.items():
            summary.append(f"- sizeof(S) <= {sizeof} : passed in registers")
            summary.append(f"- sizeof(S) >  {sizeof} : passed by ref: {passed_by_ref_value}")

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
        types, boundaries, passed_by_ref_value = self.process_results(results)

        # Summarize and output the results
        summary = self.summary_results(types, boundaries, passed_by_ref_value)
        return "\n".join(summary)

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, citeration, dtype, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

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
