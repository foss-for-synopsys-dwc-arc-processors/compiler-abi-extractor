#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

class TargetArch:
    def get_registers(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_argument_registers(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_type(self):
        raise NotImplementedError("Subclasses should implement this!")

# RISCV target specific
class RISCV(TargetArch):
    def __init__(self):
        self.Registers = [
            "zero", "ra", "sp", "gp", "tp",
            "t0", "t1", "t2", "s0", "s1",
            "a0", "a1", "a2", "a3", "a4",
            "a5", "a6", "a7", "s2", "s3",
            "s4", "s5", "s6", "s7", "s8",
            "s9", "s10", "s11", "t3", "t4",
            "t5", "t6"
        ]
        # According to RISCV ABI.
        self.ArgumentRegisters = ["a0", "a1", "a2", "a3",
                                  "a4", "a5", "a6", "a7"]

    def get_registers(self):
        return self.Registers

    def get_argument_registers(self):
        return self.ArgumentRegisters
