# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import analyzer
import helper
import hexUtils
import dumpInformation

"""
The purpose of this class is to generate a variety of C test cases using
different fundamental C types for argument passing.

Given a specified argument count value, several hexadecimal values will be
passed to a `callee` function written in assembly, which saves all register
values and prints them to stdout at the end.

For instance, using `int` as the datatype and 4 as argument count,
we have the following example:
```c
    extern void callee(int, int, int, int);

    int main(void) {
        callee(0x12345678, 0x12345678, 0x12345678, 0x12345678);
    }
```

Note that for certain datatypes, an auxiliary function is created to convert
the value of one datatype to another. For example, for the `double` datatype,
the test case is as follows:
```c
    #include <string.h>

    inline static double ull_as_double(unsigned long long lhs) {
        double result;
        memcpy(&result, &lhs, sizeof(result));
        return result;
    }

    extern void callee(double, double, double, double);

    int main(void) {
        callee(ull_as_double(0x1234567890abcdef), ull_as_double(0x1234567890abcdef),
            ull_as_double(0x1234567890abcdef), ull_as_double(0x1234567890abcdef));
    }
```
Hexadecimal values like `0x1234567890abcdef` are typically interpreted as
integer types in C, such as `unsigned long long`.

When dealing with different datatypes like `double`, we need to be aware that
although both `unsigned long long` and `double` may occupy the same number
of bits (64 bits), their bit-level representations are different.

The convertion function `ull_as_double` uses `memcpy` to directly copy the
bit pattern of the `unsigned long long` into a `double`. This does not change
the bit values themselves but reinterprets them according to the
IEEE 754 standard for a `double`.

Without this convertion function, the compiler would not know to correctly
interpret the 64-bit pattern as a `double` and will likely change the
hexadecimal value.
"""


class ArgPassGenerator:
    def __init__(self, Target):
        self.Target = Target
        self.Result = []

    def append(self, W):
        self.Result.append(W)

    def get_result(self):
        return "\n".join(self.Result)

    def generate_include(self):
        self.append("#include <string.h>")

    def generate_as_double(self):
        self.append(
            """
inline static double ull_as_double(unsigned long long lhs) {
    double result;
    memcpy(&result, &lhs, sizeof(result));
    return result;
}
"""
        )

    def generate_as_float(self):
        self.append(
            """
inline static float int_as_float(unsigned int lhs) {
    float result;
    memcpy(&result, &lhs, sizeof(result));
    return result;
}
"""
        )

    def generate_converter(self, dtype):
        if dtype == "double":
            self.generate_include()
            self.generate_as_double()
        elif dtype == "float":
            self.generate_include()
            self.generate_as_float()

    def generate_main(self, dtype, argv):
        types_list = [dtype] * len(argv)
        types_str = ", ".join(types_list)

        if dtype == "double":
            argv_str = ", ".join(f"ull_as_double({value})" for value in argv)
        elif dtype == "float":
            argv_str = ", ".join(f"int_as_float({value})" for value in argv)
        else:
            argv_str = ", ".join(argv)

        self.append(
            """
extern void callee(%s);

int main(void) {
    callee(%s);
}
"""
            % (types_str, argv_str)
        )

    def generate(self, dtype, argv):
        self.generate_converter(dtype)
        self.generate_main(dtype, argv)

        return self.get_result()


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


class ArgPassTests:
    def __init__(self, Target):
        self.Target = Target
        self.results = []

    # e.g
    # { "dtype": [double], "argc": 1, "regs": [fa0], "order": None, "inconsistencies": None, "stack": None }
    # ...
    # { "dtype": [double], "argc": 9, "regs": [a0, a1], "order": [low, high], "inconsistencies": None, "stack": None }
    # ...
    # { "dtype": [double], "argc": 13, "regs": None, "order": [low, high], "inconsistencies": None, "stack": True }
    def process_stage1(self, results):
        types = []
        for dtype, iterations in results.items():
            dtype = dtype.replace(" ", "_")

            duplicates = set()
            for citeration in iterations:
                argc = citeration["argc"]
                # Filter out duplicates from registers
                regs = [
                    item
                    for item in citeration["registers"]
                    if item not in duplicates
                ]
                order = citeration["pairs_order"]
                inconsistencies = citeration["inconsistencies"]
                stack = True if citeration["value_in_stack"] else False

                types.append(
                    {
                        "dtypes": [dtype],
                        "argc": argc,
                        "regs": regs,
                        "order": order,
                        "inconsistencies": inconsistencies,
                        "stack": stack,
                    }
                )

                duplicates.update(citeration["registers"])

        return types

    # e.g
    # { "char": [
    #   { "args": [1,2,3,4,5,6,7,8], "regs": [a0,a1,a2,a3,a4,a5,a6,a7], "order": None, "stack": None },
    #   { "args": [9], "regs": None, "order": None, "stack": True }],
    #   "int": [
    #   { "args": [1,2,3,4,5,6,7,8], "regs": [a0,a1,a2,a3,a4,a5,a6,a7], "order": None, "stack": None },
    #   { "args": [9], "regs": None, "order": None, "stack": True }],
    #   "double": [
    #   { "args": [1,2,3,4,5,6,7,8], "regs": [fa0,fa1,fa2,fa3,fa4,fa5,fa6,fa7], "order": None, "stack": None },
    #   { "args": [9,10,11,12], "regs": [a0,a1,a2,a3,a4,a5,a6,a7], "order": [low, high], "stack": None }
    #   { "args": [13], "regs": None, "order": [low, high], "stack": True }]
    # }
    def process_stage2(self, types):
        result = {}
        for x in types:
            dtypes_k = " ".join(x["dtypes"])

            # Create a new entry if the key does not exist
            if dtypes_k not in result:
                result[dtypes_k] = []

            for y in result[dtypes_k]:
                if y["order"] == x["order"] and y["stack"] == x["stack"]:
                    y["args"].append(x["argc"])
                    y["regs"].extend(x["regs"])
                    break
            else:
                # If no matching entry was found, create a new one
                result[dtypes_k].append(
                    {
                        "args": [x["argc"]],
                        "regs": x["regs"],
                        "order": x["order"],
                        "inconsistencies": x["inconsistencies"],
                        "stack": x["stack"],
                    }
                )

        return result

    # e.g
    # { "char int": [
    #   { "args": [1,2,3,4,5,6,7,8], "regs": [a0,a1,a2,a3,a4,a5,a6,a7], "order": None, "stack": None },
    #   { "args": [9], "regs": None, "order": None, "stack": True }],
    #   "double": [
    #   { "args": [1,2,3,4,5,6,7,8], "regs": [fa0,fa1,fa2,fa3,fa4,fa5,fa6,fa7], "order": None, "stack": None },
    #   { "args": [9,10,11,12], "regs": [a0,a1,a2,a3,a4,a5,a6,a7], "order": [low, high], "stack": None }
    #   { "args": [13], "regs": None, "order": [low, high], "stack": True }]
    # }
    def process_stage3(self, result):
        merged_r = {}
        for dtype, data in result.items():
            existing_dtype = None
            for merged_dtype, merged_data in merged_r.items():
                if merged_data == data:
                    existing_dtype = merged_dtype
                    break

            if existing_dtype:
                new_dtype = existing_dtype + " " + dtype
                merged_r[new_dtype] = merged_r.pop(existing_dtype)
            else:
                merged_r[dtype] = data

        return merged_r

    def process_summary(self, result):
        # e.g
        # n = [1,2,3,4,5,6,7,8]
        # return 1-8
        def array_to_range(n):
            if len(n) == 1:
                return str(n[0])
            if all(n[i] + 1 == n[i + 1] for i in range(len(n) - 1)):
                return f"{n[0]}-{n[-1]}"
            return ", ".join(map(str, n))

        r = ["Argument passing test:"]

        # e.g
        # - char : int
        #   - args 1-8 : a0 a1 a2 a3 a4 a5 a6 a7
        #   - args 9   : [stack]
        # - double
        #   - args 1-8 : fa0 fa1 fa2 fa3 fa4 fa5 fa6 fa7
        #   - args 9-12 [low, high]: [a0 a1] [a2 a3] [a4 a5] [a6 a7]
        #   - args 13  : [stack]
        for k, v in result.items():
            r.append(f"- {' : '.join(k.split())}")

            inconsistencies = []
            for x in v:
                # Create a list of inconsistencies from dtype if any.
                if x["inconsistencies"]:
                    inconsistencies.extend(x["inconsistencies"])

                # e.g
                # old -> args 9-12 [low, high]: a0 a1 a2 a3 a4 a5 a6 a7
                # new -> args 9-12 [low, high]: [a0 a1] [a2 a3] [a4 a5] [a6 a7]
                if not x["stack"]:
                    if x["order"]:
                        order_str = x["order"]
                        regs = x["regs"]
                        regs_str = " ".join(
                            [
                                f"[{regs[i]}, {regs[i+1]}]"
                                for i in range(0, len(regs), 2)
                            ]
                        )
                    else:
                        order_str = ""
                        regs_str = (
                            " ".join(x["regs"])
                            if x["regs"]
                            else "[stack]" if x["stack"] else ""
                        )
                else:
                    regs_str = "[stack]"

                r.append(
                    f" - args {array_to_range(x['args']):<3} {order_str}: {regs_str}"
                )

            # e.g
            # inconsistencies = [ ("t0", "[stack]"), ("t1", "a1") ]
            #  - WARNING: multiple value occurrences detected in (t0, [stack]), (t1, a1)
            if inconsistencies:
                inconsistency_str = ", ".join(
                    map(str, inconsistencies)
                ).replace("'", "")
                r.append(
                    f" - WARNING: multiple value occurrences detected in {inconsistency_str}"
                )

        r.append("")
        return "\n".join(r)

    def process_stages(self, results):
        results = self.process_stage1(results)
        results = self.process_stage2(results)
        results = self.process_stage3(results)
        results = self.process_summary(results)
        return results

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Argument count value
        argc = len(argv)

        # Initialize current test details
        citeration = {
            "argc": argc,  # Argument count
            "argv": argv,  # Value checked
            "registers": None,  # Registers containing the value
            "value_in_stack": None,  # Wether the value is in the stack
            "pairs_order": None,  # Order of split values (if any)
            "inconsistencies": None,  # Multiple value occurrences detected
        }

        # Check if the value is in the registers and update current test
        registers, inconsistencies = hutils.find_registers_fill(
            argv.copy(), register_banks
        )
        citeration["registers"], citeration["inconsistencies"] = (
            registers,
            inconsistencies,
        )

        registers, inconsistencies, pairs_order = hutils.find_registers_pairs(
            argv.copy(), register_banks
        )
        if registers:
            if not citeration.get("registers"):
                citeration["registers"] = registers
            else:
                citeration["registers"].update(registers)

        if inconsistencies:
            if not citeration.get("inconsistencies"):
                citeration["inconsistencies"] = registers
            else:
                citeration["inconsistencies"].update(inconsistencies)

        if pairs_order:
            if not citeration.get("pairs_order"):
                citeration["pairs_order"] = pairs_order
            else:
                citeration["pairs_order"].update(pairs_order)

        # Check if the value is in the stack and update current test
        value_in_stack, inconsistencies = hutils.find_value_fill_in_stack(
            citeration, argv.copy(), stack
        )
        citeration["value_in_stack"] = value_in_stack
        citeration["inconsistencies"] = inconsistencies

        # If value was not found in the stack, check for pairs in the stack
        if not citeration["value_in_stack"]:
            value_in_stack, inconsistencies = hutils.find_value_pairs_in_stack(
                citeration, argv.copy(), stack
            )
            citeration["value_in_stack"] = value_in_stack
            citeration["inconsistencies"] = inconsistencies

        # Convert registers to a list if its a dictionary
        if not isinstance(citeration["registers"], list):
            citeration["registers"] = list(citeration["registers"].keys())

        return citeration


class ArgPassAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "argpass")

    def analyze(self):
        # List of datatypes to be tested.
        types = ["char", "short", "int", "long", "long long", "float", "double"]

        results = {}
        for dtype in types:
            # Create an instance of `ArgPassTests` for the current Target
            arg_pass_tests = ArgPassTests(self.Target)

            dtype_sizeof = self.Target.get_type_details(dtype)["size"]
            results[dtype] = []

            argc = 1
            while True:
                # Generate hexadecimal values for the current datatype and count
                helper.reset_used_values()
                argv = helper.generate_hexa_list(argc, dtype_sizeof)

                # Generate the content of the test file.
                stdout = self.generate(
                    ArgPassGenerator(self.Target).generate(dtype, argv)
                )

                # Parse the stdout to extract stack and register bank information.
                dump_information = dumpInformation.DumpInformation()
                dump_information.parse(stdout)

                for (
                    bank_id,
                    reg_info,
                ) in dump_information.get_reg_bank_infos().items():
                    self.Target.set_register_size(bank_id, reg_info["size"])

                # Get the stack and register bank information
                stack = dump_information.get_stack()
                reg_banks = dump_information.get_reg_banks()
                # Run the test to check if the value is in the stack
                citeration = arg_pass_tests.run_test(stack, reg_banks, argv)

                results[dtype].append(citeration)
                if citeration["value_in_stack"]:
                    break

                if argc == 20:
                    print("DEBUG: Exitting for save purposes. [do_argpas]")
                    break

                argc += 1

            if dtype == "int":
                self.Target.set_argument_registers(citeration["registers"])

        # Process the results
        return arg_pass_tests.process_stages(results)
