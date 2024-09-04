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

class ReturnTests:
    def __init__(self, Target):
        self.Target = Target

    def generate_summary(self, results):
        register_dict = {}
        pairs_order = ""

        for key, value in results.items():
            fill = tuple(value[0]['registers_fill'])
            pairs = tuple(value[0]['registers_pairs'])

            if not pairs_order:
                pairs_order = value[0]["pairs_order"]

            if fill and not pairs:
                if fill not in register_dict:
                    register_dict[fill] = []
                register_dict[fill].append(key)
            elif pairs and not fill:
                if pairs not in register_dict:
                    register_dict[pairs] = []
                register_dict[pairs].append(key)
            else:
                if () not in register_dict:
                    register_dict[()] = []
                register_dict[()].append(key)

        summary = ["Return registers:"]

        for regs, types in register_dict.items():
            if regs:
                if len(regs) == 1:
                    # Single register
                    summary.append(f"- {' : '.join(types)}")
                    summary.append(f" - passed in registers: {', '.join([f'{reg}' for reg in regs])}")
                else:
                    # Paired registers
                    summary.append(f"- {' : '.join(types)}")
                    summary.append(f" - passed in registers {pairs_order}: {', '.join([f'{reg}' for reg in regs])}")
            else:
                # No registers
                summary.append(f"- {' : '.join(types)}")
                summary.append(" - passed in registers: None")

        summary.append("")
        return "\n".join(summary)

    def run_test(self, citeration, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)
        argv = [argv]

        tmp = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers_fill"], citeration["inconsistencies"] = tmp

        tmp = hutils.find_registers_pairs(argv.copy(), register_banks)
        citeration["registers_pairs"], citeration["inconsistencies"], citeration["pairs_order"] = tmp

        return citeration