#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This class is responsible for a set of utility
functions for handling hexadecimal values.
"""

class HexUtils:
    def __init__(self, target, current_test):
        self.Target = target

    # Remove '0x' prefix.
    def _remove_identifier(self, value):
        return value[2:]

    # Add '0x' prefix.
    def _add_identifier(self, value):
        return f"0x{value}"
