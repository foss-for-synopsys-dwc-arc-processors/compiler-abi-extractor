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

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Argument count value
        argc = len(argv)

        # Initialize current test details
        citeration = {
            "argc": argc,               # Argument count
            "argv": argv,               # Value checked
            "registers": None,          # Registers containing the value
            "value_in_stack": None,     # Wether the value is in the stack
            "pairs_order": None,        # Order of split values (if any)
            "inconsistencies": None     # Multiple value occurrences detected
        }

        # Check if the value is in the registers and update current test
        registers, inconsistencies = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers"], citeration["inconsistencies"] = registers, inconsistencies

        registers, inconsistencies, pairs_order = hutils.find_registers_pairs(argv.copy(), register_banks)
        if registers:
            if not citeration.get("registers"):
                citeration["registers"] = registers
            else:
                citeration["registers"].update(registers)

        if inconsistencies:
            if not citeration.get("inconsistencies"):
                citeration["inconsistencies"] = registers
            else:
                citeration["inconsistencies"].update(inconsistencies)

        if pairs_order:
            if not citeration.get("pairs_order"):
                citeration["pairs_order"] = pairs_order
            else:
                citeration["pairs_order"].update(pairs_order)

        # Check if the value is in the stack and update current test
        value_in_stack, inconsistencies = hutils.find_value_fill_in_stack(citeration, argv.copy(), stack)
        citeration["value_in_stack"] = value_in_stack
        citeration["inconsistencies"] = inconsistencies

        # If value was not found in the stack, check for pairs in the stack
        if not citeration["value_in_stack"]:
            value_in_stack, inconsistencies = hutils.find_value_pairs_in_stack(citeration, argv.copy(), stack)
            citeration["value_in_stack"] = value_in_stack
            citeration["inconsistencies"] = inconsistencies

        # Convert registers to a list if its a dictionary
        if not isinstance(citeration["registers"], list):
            citeration["registers"] = list(citeration["registers"].keys())

        return citeration

import sys
if __name__ == "__main__":
    pass
