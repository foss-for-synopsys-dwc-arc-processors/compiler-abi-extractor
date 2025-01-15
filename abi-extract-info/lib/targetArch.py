#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

class TargetArch:
    def __init__(self):
        self.type_details = dict()
        self.argument_registers = []
        self.register_bank_count = 0

    def set_type_details(self, type_details):
        self.type_details = type_details

    def get_type_details(self, datatype):
        return self.type_details[datatype]

    def set_argument_registers(self, registers):
         self.argument_registers = registers

    def get_argument_registers(self):
        return self.argument_registers

    def set_register_bank_count(self, register_bank_count):
        self.register_bank_count = register_bank_count

    def get_register_bank_count(self):
        return self.register_bank_count

    def get_registers(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_type(self):
        raise NotImplementedError("Subclasses should implement this!")

# RISCV target specific
class RISCV(TargetArch):
    def __init__(self):
        super().__init__()
        self.Registers = {
            "regs_bank0": [
                "zero", "ra", "sp", "gp", "tp",
                "t0", "t1", "t2", "s0", "s1",
                "a0", "a1", "a2", "a3", "a4",
                "a5", "a6", "a7", "s2", "s3",
                "s4", "s5", "s6", "s7", "s8",
                "s9", "s10", "s11", "t3", "t4",
                "t5", "t6"
            ],
            "regs_bank1": [
                "ft0", "ft1", "ft2", "ft3", "ft4",
                "ft5", "ft6", "ft7", "fs0", "fs1",
                "fa0", "fa1", "fa2", "fa3", "fa4",
                "fa5", "fa6", "fa7", "fs2", "fs3",
                "fs4", "fs5", "fs6", "fs7", "fs8",
                "fs9", "fs10", "fs11", "ft8", "ft9",
                "ft10", "ft11"
            ]
        }

    def get_registers(self, key = None):
        if key and key in self.Registers:
            return self.Registers[key]

        return self.Registers
