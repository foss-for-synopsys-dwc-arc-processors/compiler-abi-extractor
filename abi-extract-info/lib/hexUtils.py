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

   # Calculate the number of bytes of `value`
    def _get_byte_count(self, value):
        hex_clean = value
        if "0x" in value:
            # Remove the '0x' prefix
            hex_clean = self._remove_identifier(value)
        # Count the number of hexadecimal digits
        hex_length = len(hex_clean)
        # Calculate the number of bytes (2 hex digits per byte)
        num_bytes = (hex_length + 1) // 2
        return num_bytes

    # Split a hexadecimal value into two halves.
    def _split_hex_value(self, value):
        value = self._remove_identifier(value) # Remove '0x' prefix
        midpoint = len(value) // 2
        first_half = f"0x{value[:midpoint]}"
        second_half = f"0x{value[midpoint:]}"
        return first_half, second_half
