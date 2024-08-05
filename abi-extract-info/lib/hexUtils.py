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

    # Retrieve the list of register indices holding a specific value from the register banks.
    def _find_register_indices(self, value, register_banks):
        indices = [
            i for register_bank in register_banks.values()
            for i, v in enumerate(register_bank)
            if v == value
        ]
        return sorted(indices)

    # Retrieve the list of registers corresponding to the given indices.
    def _get_registers_by_indices(self, indices):
        return [self.Target.get_registers()[i] for i in indices]

    # Find registers that hold the split halves of a value.
    def _find_registers_for_split_value(self, first_half, second_half, register_banks):
        indices = self._find_register_indices(first_half, register_banks) + \
                  self._find_register_indices(second_half, register_banks)

        if not indices:
            return None

        indices = sorted(set(indices))  # Remove duplicates and sort

        # Determine the order of the split values
        first_index_value = list(register_banks.values())[0][indices[0]]
        if first_index_value == first_half:
            self.current_test["value_split_order"] = ["[High]", "[Low]"]
        else:
            self.current_test["value_split_order"] = ["[Low]", "[High]"]

        return self._get_registers_by_indices(indices)

# Extend the given hex value to the specified `argc` and return list of hex values.
    def _extend_value_to_argc(self, value, argc):
        # Retrieve the size of an `int` in bytes to know the size of a register.
        int_byte_count = self.Target.get_type_details("int")["size"]

        # Remove hexa identifier.
        _value = self._remove_identifier(value)
        extended_value = []

        # Extend the value by repeating it `argc` times.
        _value = _value * argc

        # Calculate the total number of bytes in the extended value.
        total_byte_count = self._get_byte_count(_value)
        remains = []

        # Split the extended value into chunks of `int_byte_count` bytes.
        while total_byte_count > int_byte_count:
            # Update the total by count.
            total_byte_count -= int_byte_count
            # Extract the remaining portion of the value.
            # e.i: If we have a register size of 4 bytes, and the extended
            # value is greater, we need to split the values into two (or more) chunks and search them in the register banks.
            #   Value        : `0x1212121212``
            #   First chunk  : `0x12121212`
            #   Second chunk : `0x12`
            remains = _value[total_byte_count*2:]

            # Update the value to exclude the extracted portion.
            _value = _value[:total_byte_count*2]

        if remains:
            remains = self._add_identifier(remains)
            extended_value.append(remains)

        value = self._add_identifier(_value)
        extended_value.append(value)

        return extended_value

  # Retrieve the list of registers that hold the given value from the register banks.
    def find_registers_for_value(self, value, register_banks):
        indices = self._find_register_indices(value, register_banks)
        return self._get_registers_by_indices(indices)

    # Find the registers holding the value or its split halves.
    def find_value_in_registers(self, value, register_banks, argc):
        # First, try to find the exact value.
        registers = self.find_registers_for_value(value, register_banks)
        if registers:
            return registers

        # If not found, check for split halves
        first_half, second_half = self._split_hex_value(value)
        registers = self._find_registers_for_split_value(first_half, second_half, register_banks)
        if registers:
            return registers

        # if neither the exact value nor its split halves are found,
        # extend the value to accomodate the specified number of
        # argument (argc)
        registers = []
        values = self._extend_value_to_argc(value, argc)
        # For each extended value, attemp to locate it in the register banks
        for v in values:
            registers += self.find_registers_for_value(v, register_banks)

        return registers
