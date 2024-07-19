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
