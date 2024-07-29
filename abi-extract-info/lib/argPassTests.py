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

class ArgPassTests:
    def __init__(self, Target):
        self.Target = Target

    # Find registers that hold the split halves of a value.
    def find_registers_for_split_value(self, first_half, second_half, register_banks):
        indexes = [
            i for register_bank in register_banks.values()
            for i, v in enumerate(register_bank) if v == first_half or v == second_half
        ]
        indexes.sort()

        # Determine the order of the split values
        first_index_value = list(register_banks.values())[0][indexes[0]]
        if first_index_value == first_half:
            self.current_test["value_split_order"] = ["[High]", "[Low]"]
        else:
            self.current_test["value_split_order"] = ["[Low]", "[High]"]
        registers = [self.Target.get_registers()[i] for i in indexes]
        return registers

    # Retrieve the list of registers that hold the given value from the register banks.
    def get_registers_for_value(self, value, register_banks):
        indexes = [
            i for register_bank in register_banks.values()
            for i, v in enumerate(register_bank) if v == value
        ]
        registers = [self.Target.get_registers()[i] for i in indexes]
        return registers

    # Split a hexadecimal value into two halves.
    def _split_hex_value(self, value):
        value = value[2:]  # Remove '0x' prefix
        midpoint = len(value) // 2
        first_half = f"0x{value[:midpoint]}"
        second_half = f"0x{value[midpoint:]}"
        return first_half, second_half

    # Find the registers holding the value or its split halves.
    def find_value_in_registers(self, value, register_banks):
        registers = self.find_registers_for_value(value, register_banks)
        if not registers:
            first_half, second_half = self._split_hex_value(value)
            registers = self.find_registers_for_split_value(first_half, second_half, register_banks)
        return registers

    def if_value_found_in_stack(self, stack, reg_banks, values_list):
        target_value = values_list[0]
        stack_value = stack[0]

        # Check if the target value matches the stack value.
        if target_value == stack_value:
            self._print_registers_for_value(target_value, reg_banks)
            return True

        # Split target value if it doesnt match the stack value.
        first_half, second_half = self._split_hex_value(target_value)

        if first_half == stack_value or second_half == stack_value:
            self._print_registers_for_value(first_half, reg_banks)
            self._print_registers_for_value(second_half, reg_banks)
            return True

        return False

def if_value_found_in_stack(Target, stack, reg_banks, value_list):
    return ArgPassTests(Target).if_value_found_in_stack(stack, reg_banks, value_list)

import sys
if __name__ == "__main__":
    pass
