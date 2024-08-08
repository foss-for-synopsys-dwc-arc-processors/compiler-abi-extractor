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
    def __init__(self, target):
        self.Target = target

    # Remove '0x' prefix.
    def _remove_identifier(self, value):
        return value[2:]

    # Add '0x' prefix.
    def _add_identifier(self, value):
        return f"0x{value}"

   # Calculate the number of bytes of `value`
    def _sizeof(self, value):
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
        total_byte_count = self._sizeof(_value)
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

    # Check if the value or its split halves are present in the stack.
    def is_value_in_stack(self, value, stack_values):
        # Currently only validating the first address of the stack.
        # Please update this. FIXME
        if value == stack_values[0]:
            return True

        first_half, second_half = self._split_hex_value(value)
        return first_half == stack_values[0] or second_half == stack_values[0]

    # Validate if the stack address has been found in the argument registers.
    def is_passed_by_ref(self, stack_address, register_banks):
        registers = set(self.find_registers_for_value(stack_address, register_banks))
        arg_registers = set(self.Target.get_argument_registers())

        # Check if there is any overlap between the found registers and argument registers
        return not registers.isdisjoint(arg_registers)

    # Finds the complete argument values in the register banks.
    def find_registers_fill(self, argv, register_banks):
        indexes = []

        # Iterate through each value in argv.
        while (argv):
            value = argv.pop(0)

            # Search for the value in each register bank.
            for bank_name, bank_register in register_banks.items():
                for index, register_value in enumerate(bank_register):
                    if register_value == value:
                        # Append the index of the value in the register bank.
                        indexes.append(index)

        return indexes

    # Finds registers that match either half of a value in `argv`.
    def find_registers_pairs(self, argv, register_banks):
        indexes = []

        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        # Process `argv` to find matching register values.
        while argv:
            value = argv.pop(0)
            sizeof_value = self._sizeof(value)

            # Split the value if its size exceeds `sizeof_int`
            if sizeof_value > sizeof_int:
                first_half, second_half = self._split_hex_value(value)

                # Search for each half in each register bank.
                for bank_name, bank_register in register_banks.items():
                    for index, register_value in enumerate(bank_register):
                        # TODO Get the order of [low] and [high]
                        if register_value == first_half:
                            indexes.append(index)
                        elif register_value == second_half:
                            indexes.append(index)
                continue

        return indexes

    # Finds registers that match combined values in `argv`.
    def find_registers_combined(self, argv, register_banks):
        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        indexes = []

        # Process `argv` to combine values.
        while (argv):
            # Peek the value from `argv`
            value = argv[0]
            res = []

            # Check if the current value is already of the expected size.
            if self._sizeof(value) == sizeof_int:
                argv.pop(0)
                continue

            # Aggregate values until the combined size reaches or exceeds sizeof_int
            while argv and self._sizeof(self._combine_hex_values(res)) < sizeof_int:
                res.append(argv.pop(0))

                if argv:
                    next_value = argv[0]
                    # Check if combining with the next value fits within `sizeof_int`
                    if self._sizeof(self._combine_hex_values(res)) + self._sizeof(next_value) <= sizeof_int:
                        res.append(argv.pop(0))
                    else:
                        break

            # Special case for combining values - `char`, `short`
            # When we are passing a `struct {char, short}`, the char value will be extended
            # to align with short.
            if len(res) == 2 and self._sizeof(res[0]) == 1 and self._sizeof(res[1]) == 2:
                res[0] = f"0x00{res[0][2:]}"  # Adjust representation for short exception.

            # Combine the aggregated values into a single hexadecimal value.
            combined_hex = self._combine_hex_values(res)

            # Search for the combined hexadecimal value in each register bank.
            for bank_name, bank_register in register_banks.items():
                for index, register_value in enumerate(bank_register):
                    if register_value == combined_hex:
                        indexes.append(index)


        return indexes

    # Finds a reference pointer of the stack in the argument registers with complete value.
    def find_ref_in_stack_fill(self, citeration, argv, register_banks, stack):
        citeration["passed_by_ref"] = None

        # Build a dictionary of register-values from the register banks.
        registers = self.Target.get_registers()
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            for index, reg in enumerate(registers):
                register_values_dict[reg] = register_values[index]

        # Iterate over stack to find matching pairs.
        for index, stack_tuple in enumerate(stack):
            # Get the index's stack address and correspoding value.
            stack_address, stack_value = stack_tuple

            # If the current stack address is in the first argument register. (FIXME Cant be hardcoded.)
            # We only taking into account the first register, because it has been observed that the
            # compiler might use another of the argument registers to store a stack address to load
            # the values into the first argument register before the actual function call.
            # i.e it first stores the values into the stack, then loads it to register.
            if register_values_dict["x10"] == stack_address:
                # FIXME Here it would make sense to validate the next stack value,
                # but has been observe that the next value is not always in the next stack address.
                if stack_value == argv[0]:
                    citeration["passed_by_ref_register"] = ["x10"] # FIXME hardcoded..
                    diff = self._hex_difference(stack[0][0], stack[index][0])
                    citeration["passed_by_ref"] = f"sp + {diff}"

                    return citeration
        return citeration

    # Finds a reference pointer of the stack in the argument registers with the expected argv.
    def find_ref_in_stack_pairs(self, citeration, argv, register_banks, stack):
        citeration["passed_by_ref"] = None
        # FIXME Assume sizeof(int) is 4  bytes; this should be dynamic if the size can change (i.e 64bits).
        sizeof_int = 4

        # Build a dictionary of register-values from the register banks.
        registers = self.Target.get_registers()
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            for index, reg in enumerate(registers):
                register_values_dict[reg] = register_values[index]

        while (argv):
            value = argv.pop(0)

            # Get the size of the current value.
            sizeof_value = self._sizeof(value)

            # Check if makes sense to split the value.
            if sizeof_value <= sizeof_int:
                continue
            # Split the value into two parts.
            first_half, second_half = self._split_hex_value(value)

            # Iterate over stack to find matching pairs.
            for index in range(len(stack) - 1): # Use len(stack) -1 to prevent out-of-range error
                # Get the index's stack address and correspoding value.
                stack_address, stack_value = stack[index]

                # If the current stack address is in the first argument register. (FIXME Cant be hardcoded.)
                # We only taking into account the first register, because it has been observed that the
                # compiler might use another of the argument registers to store a stack address to load
                # the values into the first argument register before the actual function call.
                # i.e it first stores the values into the stack, then loads it to register.
                if register_values_dict["x10"] == stack_address:
                    # FIXME Here it would make sense to validate the next stack value,
                    # but has been observe that the next value is not always in the next stack address.
                    if stack_value == first_half or stack_value == second_half:
                        citeration["passed_by_ref_register"] = ["x10"] # FIXME harcoded..
                        diff = self._hex_difference(stack[0][0], stack[index][0])
                        citeration["passed_by_ref"] = f"sp + {diff}"

                        return citeration

        return citeration

    def find_ref_in_stack_combined(self, citeration, argv, register_banks, stack):
        citeration["passed_by_ref"] = None
        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        # Build a dictionary of register-values from the register banks.
        registers = self.Target.get_registers()
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            for index, reg in enumerate(registers):
                register_values_dict[reg] = register_values[index]

        # Process argv to combine values.
        while (argv):
            # Peek the value from argv
            value = argv[0]
            res = []
            # Aggregate values until the combined size reaches or exceeds sizeof_int.
            while argv and self._sizeof(self._combine_hex_values(res)) < sizeof_int:
                res.append(argv.pop(0))

                # Check if adding the next would still fit within `sizeof_int`.
                if argv:
                    next_value = argv[0]
                    if self._sizeof(self._combine_hex_values(res)) + self._sizeof(next_value) <= sizeof_int:
                        res.append(argv.pop(0))
                    else:
                        break

            # Special case for combining values - `char`, `short`
            # When we are passing a `struct {char, short}`, the char value will be extended
            # to align with short.
            if len(res) == 2 and self._sizeof(res[0]) == 1 and self._sizeof(res[1]) == 2:
                res[0] = f"0x00{res[0][2:]}"  # Adjust representation for short exception.

            # Combine the aggregated values into a single hexadecimal value.
            combined_hex = self._combine_hex_values(res)

            # Iterate over the stack to find a matching reference.
            for index in range(len(stack)):
                if index > len(stack) - 1:
                    break

                # Here instead of checking all positions in the stack,
                # we only care about the first one.
                stack_address, stack_value = stack[index]
                if register_values_dict["x10"] == stack_address:
                    if stack_value == combined_hex:
                        citeration["passed_by_ref_register"] = ["x10"]
                        diff = self._hex_difference(stack[0][0], stack[index][0])
                        citeration["passed_by_ref"] = f"sp + {diff}"

                        return citeration

        return citeration
