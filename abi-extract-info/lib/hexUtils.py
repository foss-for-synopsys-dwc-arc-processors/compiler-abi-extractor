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

from lib import helper

class HexUtils:
    def __init__(self, target):
        self.Target = target

    # Remove '0x' prefix.
    def _remove_identifier(self, value):
        return value[2:]

    # Add '0x' prefix.
    def _add_identifier(self, value):
        return f"0x{value}"

    # Calculate the difference between two hexadecimal strings.
    def _hex_difference(self, hex1: str, hex2: str) -> int: # Shall I adapt to this?
        # Convert hexadecimal strings to integers.
        num1 = int(hex1, 16)
        num2 = int(hex2, 16)

        # Compute the difference.
        difference = abs(num1 - num2)

        return difference

   # Calculate the number of bytes of `value`
    def sizeof(self, value):
        hex_clean = value
        if "0x" in value:
            # Remove the '0x' prefix
            hex_clean = self._remove_identifier(value)
        # Count the number of hexadecimal digits
        hex_length = len(hex_clean)
        # Calculate the number of bytes (2 hex digits per byte)
        num_bytes = (hex_length + 1) // 2
        return num_bytes

    # Combine hexadecimal values i.e 0x1234 + 0x5678 = 0x56781234
    def _combine_hex_values(self, hex_values, endianness="little_endian"):
        if endianness == "little_endian":
            concatenated = "".join(h[2:] for h in reversed(hex_values))
        elif endianness == "big_endian":
            concatenated = "".join(h[2:] for h in hex_values)

        combined_hex = "0x" + concatenated
        return combined_hex

    # Split a hexadecimal value into two halves.
    def _split_hex_value(self, value):
        value = self._remove_identifier(value) # Remove '0x' prefix
        midpoint = len(value) // 2
        first_half = f"0x{value[:midpoint]}"
        second_half = f"0x{value[midpoint:]}"
        return first_half, second_half

    # Extend a value as zero or sign extended.
    def _zero_or_sign_extend(self, value, sizeof_int, is_zero):
        value = self._remove_identifier(value)
        type_extend = "00" if is_zero else "ff"

        while (self.sizeof(value) < sizeof_int):
            value = f"{type_extend}{value}"

        value = self._add_identifier(value)
        return value

    def _zero_extend(self, value, sizeof):
        is_zero = True
        hvalue = self._zero_or_sign_extend(value, sizeof, is_zero)
        return hvalue

    def _sign_extend(self, value, sizeof):
        is_zero = False
        hvalue = self._zero_or_sign_extend(value, sizeof, is_zero)
        return hvalue

    # Finds the complete argument values in the register banks.
    def find_registers_fill(self, argv, register_banks):
        registers = {}
        inconsistencies = []

        # Iterate through each value in argv.
        while (argv):
            tmp = []
            value = argv.pop(0)

            # Search for the value in each register bank.
            for bank_name, bank_register in register_banks.items():
                bank_register_names = self.Target.get_registers(bank_name)
                for index, register_value in enumerate(bank_register):

                    # Convert hexadecimal values to binary.
                    bvalue_register = helper.hexa_to_binary(register_value)
                    bvalue          = helper.hexa_to_binary(value)
                    # Convert expected value to zero extended.
                    zero_register_value = self._zero_extend(value, self.sizeof(register_value))
                    # Convert expected value to sign extended.
                    sign_register_value = self._sign_extend(value, self.sizeof(register_value))

                    if bvalue_register == bvalue or \
                       bvalue_register == helper.hexa_to_binary(zero_register_value) or \
                       bvalue_register == helper.hexa_to_binary(sign_register_value):
                        tmp.append(bank_register_names[index])
                        registers[bank_register_names[index]] = value

            if len(tmp) > 1:
                inconsistencies.append(tmp)

        return (registers, inconsistencies)

    # Finds the complete argument value in stack.
    def find_value_fill_in_stack(self, citeration, argv, stack):
        addresses = []
        inconsistencies = []

        value = argv[-1]
        for stack_address, stack_value in stack:
            # Convert hexadecimal values to binary.
            bvalue_stack = helper.hexa_to_binary(stack_value)
            bvalue       = helper.hexa_to_binary(value)

            # Convert expected value to zero extended.
            zero_stack_value = self._zero_extend(value, self.sizeof(stack_value))
            # Convert expected value to sign extended.
            sign_stack_value = self._sign_extend(value, self.sizeof(stack_value))

            if bvalue_stack == bvalue or \
                bvalue_stack == helper.hexa_to_binary(zero_stack_value) or \
                bvalue_stack == helper.hexa_to_binary(sign_stack_value):
                for k,v in citeration["registers"].items():
                    if v == value:
                        inconsistencies.append((k,"[stack]"))
                addresses.append(stack_address)

        return (addresses, inconsistencies)

    # Finds pairs of argument value in stack.
    def find_value_pairs_in_stack(self, citeration, argv, stack):
        addresses = []
        inconsistencies = []
        value = argv[-1]

        # riscv ilp32d fp registers are 64bit..
        if self.sizeof(value) < self.Target.get_type_details("int")["size"]:
            return addresses, inconsistencies

        high, low = self._split_hex_value(value)

        for stack_address, stack_value in stack:
            if stack_value in (high, low):
                for k, v in citeration["registers"].items():
                    if v == stack_value:
                        inconsistencies.append((k, "[stack]"))
                addresses.append(stack_address)

        return (addresses, inconsistencies)

    # Finds the zero or sign extended  argument values in the register banks.
    def find_registers_extended(self, argv, register_banks, is_zero):
        registers = []

        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        # Iterate through each value in argv.
        while (argv):

            value = argv.pop(0)

            # If the value is greater or equal to the register sizeof, continue.
            if self.sizeof(value) >= sizeof_int:
                continue

            value = self._zero_or_sign_extend(value, is_zero)

            # Search for the value in each register bank.
            for bank_name, bank_register in register_banks.items():
                bank_register_names = self.Target.get_registers(bank_name)
                for index, register_value in enumerate(bank_register):
                    if register_value == value:
                        # Append register.
                        registers.append(bank_register_names[index])

        return registers

    # Finds registers that match either half of a value in `argv`.
    def find_registers_pairs(self, argv, register_banks):
        registers = {}
        inconsistencies = []
        order = ""

        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        # Process `argv` to find matching register values.
        while argv:
            tmp = []
            value = argv.pop(0)
            sizeof_value = self.sizeof(value)

            # Split the value if its size exceeds `sizeof_int`
            if sizeof_value > sizeof_int:
                first_half, second_half = self._split_hex_value(value)

                # Search for each half in each register bank.
                for bank_name, bank_register in register_banks.items():
                    bank_register_names = self.Target.get_registers(bank_name)
                    for index, register_value in enumerate(bank_register):

                        # Get the order of [low] and [high]
                        if not order:
                            if register_value == first_half and bank_register[index+1] == second_half:
                                order = "[high], [low]"
                            elif register_value == second_half and bank_register[index+1] == first_half:
                                order = "[low], [high]"

                        # Convert hexadecimal values to binary.
                        bvalue_register   = helper.hexa_to_binary(register_value)
                        bvalue_first_half = helper.hexa_to_binary(first_half)
                        bvalue_second_half = helper.hexa_to_binary(second_half)

                        if bvalue_register == bvalue_first_half:
                            # Append register
                            tmp.append(bank_register_names[index])
                            registers[bank_register_names[index]] = first_half
                        elif bvalue_register == bvalue_second_half:
                            # Append register
                            tmp.append(bank_register_names[index])
                            registers[bank_register_names[index]] = second_half

                if len(tmp) > 1:
                    inconsistencies.append(tmp)
                continue

        return (registers, inconsistencies, order)

    # Finds registers that match combined values in `argv`.
    def find_registers_combined(self, argv, register_banks):
        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        registers = {}
        inconsistencies = []

        # Process `argv` to combine values.
        while (argv):
            # Peek the value from `argv`
            value = argv[0]
            res = []
            tmp = []

            # Check if the current value is already of the expected size.
            if self.sizeof(value) == sizeof_int:
                argv.pop(0)
                continue

            # Aggregate values until the combined size reaches or exceeds sizeof_int
            while argv and self.sizeof(self._combine_hex_values(res)) < sizeof_int:
                res.append(argv.pop(0))

                if argv:
                    next_value = argv[0]
                    # Check if combining with the next value fits within `sizeof_int`
                    if self.sizeof(self._combine_hex_values(res)) + self.sizeof(next_value) <= sizeof_int:
                        res.append(argv.pop(0))
                    else:
                        break

            # Special case for combining values - `char`, `short`
            # When we are passing a `struct {char, short}`, the char value will be extended
            # to align with short.
            if len(res) == 2 and self.sizeof(res[0]) == 1 and self.sizeof(res[1]) == 2:
                res[0] = f"0x00{res[0][2:]}"  # Adjust representation for short exception.

            # Combine the aggregated values into a single hexadecimal value.
            combined_hex = self._combine_hex_values(res)

            # Search for the combined hexadecimal value in each register bank.
            for bank_name, bank_register in register_banks.items():
                bank_register_names = self.Target.get_registers(bank_name)
                for index, register_value in enumerate(bank_register):
                    # Convert hexadecimal values to binary.
                    bvalue_register = helper.hexa_to_binary(register_value)
                    bvalue_combined = helper.hexa_to_binary(combined_hex)

                    if bvalue_register == bvalue_combined:
                        # Append register
                        tmp.append(bank_register_names[index])
                        registers[bank_register_names[index]] = combined_hex
            if len(tmp) > 1:
                inconsistencies.append(tmp)

        return (registers, inconsistencies)

    # Finds a reference pointer of the stack in the argument registers with complete value.
    def find_ref_in_stack_fill(self, dtype, argv, register_banks, stack):
        passed_by_ref = None
        passed_by_ref_register = None

        argument_registers = self.Target.get_argument_registers()

        # Build a dictionary of register-values from the register banks.
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            registers = self.Target.get_registers(bank_name)
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
            if register_values_dict[argument_registers[0]] == stack_address:
                # FIXME Here it would make sense to validate the next stack value,
                # but has been observe that the next value is not always in the next stack address.
                if stack_value == argv[0]:
                    passed_by_ref_register = register_values_dict[argument_registers[0]]
                    passed_by_ref = "[stack]"

                    return (passed_by_ref, passed_by_ref_register)

        return (passed_by_ref, passed_by_ref_register)

    # Finds a reference pointer of the stack in the argument registers with the expected argv.
    def find_ref_in_stack_pairs(self, dtype, argv, register_banks, stack):
        passed_by_ref = None
        passed_by_ref_register = None

        # FIXME Assume sizeof(int) is 4  bytes; this should be dynamic if the size can change (i.e 64bits).
        sizeof_int = 4

        # The reg_bank0 registers are used for the passed by reference,
        # even with floating-point register values.
        argument_registers = self.Target.get_argument_registers()

        # Build a dictionary of register-values from the register banks.
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            registers = self.Target.get_registers(bank_name)
            for index, reg in enumerate(registers):
                register_values_dict[reg] = register_values[index]

        while (argv):
            value = argv.pop(0)

            # Get the size of the current value.
            sizeof_value = self.sizeof(value)

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
                if register_values_dict[argument_registers[0]] == stack_address:
                    # FIXME Here it would make sense to validate the next stack value,
                    # but has been observe that the next value is not always in the next stack address.
                    if stack_value == first_half or stack_value == second_half:
                        passed_by_ref_register = register_values_dict[argument_registers[0]]
                        passed_by_ref = "[stack]"

                        return (passed_by_ref, passed_by_ref_register)

        return (passed_by_ref, passed_by_ref_register)

    def find_ref_in_stack_combined(self, dtype, argv, register_banks, stack):
        passed_by_ref = None
        passed_by_ref_register = None

        # FIXME Assume sizeof(int) is 4 bytes; this should be dynamic if the size can change (i.e., 64 bits).
        sizeof_int = 4

        argument_registers = self.Target.get_argument_registers()

        # Build a dictionary of register-values from the register banks.
        register_values_dict = dict()
        for bank_name, register_values in register_banks.items():
            registers = self.Target.get_registers(bank_name)
            for index, reg in enumerate(registers):
                register_values_dict[reg] = register_values[index]

        # Process argv to combine values.
        while (argv):
            # Peek the value from argv
            value = argv[0]
            res = []
            # Aggregate values until the combined size reaches or exceeds sizeof_int.
            while argv and self.sizeof(self._combine_hex_values(res)) < sizeof_int:
                res.append(argv.pop(0))

                # Check if adding the next would still fit within `sizeof_int`.
                if argv:
                    next_value = argv[0]
                    if self.sizeof(self._combine_hex_values(res)) + self.sizeof(next_value) <= sizeof_int:
                        res.append(argv.pop(0))
                    else:
                        break

            # Special case for combining values - `char`, `short`
            # When we are passing a `struct {char, short}`, the char value will be extended
            # to align with short.
            if len(res) == 2 and self.sizeof(res[0]) == 1 and self.sizeof(res[1]) == 2:
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
                if register_values_dict[argument_registers[0]] == stack_address:
                    if stack_value == combined_hex:
                        passed_by_ref_register = register_values_dict[argument_registers[0]]
                        passed_by_ref = "[stack]"

                        return (passed_by_ref, passed_by_ref_register)

        return (passed_by_ref, passed_by_ref_register)
