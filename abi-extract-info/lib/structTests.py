#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
The logic relies on validating the presence of the stack address in the
argument passing registers to ensure that we have found the boundary limits
for struct argument passing.
"""

import sys

class StructValidator:
    def __init__(self, Target):
        self.Target = Target

    # Validate if the stack address has been found in the first argument register.
    # If so, then we have reached our limits.
    def if_stack_address_found(self, stack_address, regs_bank):

        mapping = dict()
        target_argument_registers = self.Target.get_argument_registers()
        for i, r in enumerate(self.Target.get_registers()):
            mapping[r] = regs_bank[i]

        argument_register_value = mapping[target_argument_registers[0]]
        if stack_address.rstrip() in argument_register_value.rstrip():
            return True

        return False


def if_stack_address_found(stack_address, regs_bank, Target):
    return StructValidator(Target).if_stack_address_found(stack_address, regs_bank)

if __name__ == "__main__":
    # TODO: Update this outdated logic.
    StdoutFile = sys.argv[1]
    StructValidator().split_sections(StdoutFile)