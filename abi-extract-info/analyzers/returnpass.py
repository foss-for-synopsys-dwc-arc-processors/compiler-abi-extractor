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
The purpose of this generator is to create a test case
that will validate how datatype values are passed in
return calls.

It will create a call to an assembly function, which
will then call a C function that will return a
datatype value, that then all registers and stack
is dumped.

             main    (.c)
              v
             foo     (.s)
              v
             bar     (.c)
              v
            callee   (.s)

TODO `long double` with sizeof of 16 bytes needs
an alternative as (for 32bit) you cannot copy their
value directly. So you define a high and low, copy
both to an array (unsigned char bytes[16]), and then
copy that array to the actual return call.
"""


class ReturnGenerator:
    def __init__(self, Target, dtype):
        self._result = []
        self.Target = Target
        self._dtype = dtype

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_include(self):
        self.append("#include <string.h>")

    def generate_as_float(self):
        self.append(
            """
inline static float ul_as_float(unsigned long lhs)
{
    float result;
    memcpy(&result, &lhs, sizeof(float));
    return result;
}
"""
        )

    def generate_as_double(self):
        self.append(
            """
inline static double ull_as_double(unsigned long long lhs)
{
    double result;
    memcpy(&result, &lhs, sizeof(double));
    return result;
}
"""
        )

    def generate_converter(self):
        if self._dtype == "float":
            self.generate_include()
            self.generate_as_float()
        elif self._dtype == "double":
            self.generate_include()
            self.generate_as_double()

    def generate_single_call_declare(self):
        pass

    def generate_single_call_prototypes(self):
        self.append("extern void foo (void);")

    def generate_single_call_bar(self, hvalue_return):
        if self._dtype == "float":
            argv = f"ul_as_float({hvalue_return})"
        elif self._dtype == "double":
            argv = f"ull_as_double({hvalue_return})"
        else:
            argv = hvalue_return

        self.append(
            """
%s bar (void) {
    /* %s a = %s; */
    return %s;
}
"""
            % (self._dtype, self._dtype, argv, argv)
        )

    def generate_single_call_main(self):
        self.append(
            """
int main (void) {
    foo ();
    return 0;
}
"""
        )

    def generate_single_call(self, hvalue_return):
        self.generate_converter()

        self.generate_single_call_prototypes()
        self.generate_single_call_bar(hvalue_return)
        self.generate_single_call_main()

        return self.get_result()


"""
This class is responsible for generating the summary report
and the proper calls to validate each dump information.
"""


class ReturnTests:
    def __init__(self, Target):
        self.Target = Target

    def generate_summary(self, results):
        register_dict = {}
        pairs_order = ""

        for key, value in results.items():
            fill = tuple(value[0]["registers_fill"])
            pairs = tuple(value[0]["registers_pairs"])

            if not pairs_order:
                pairs_order = value[0]["pairs_order"]

            if fill and not pairs:
                if fill not in register_dict:
                    register_dict[fill] = []
                register_dict[fill].append(key)
            elif pairs and not fill:
                if pairs not in register_dict:
                    register_dict[pairs] = []
                register_dict[pairs].append(key)
            else:
                if () not in register_dict:
                    register_dict[()] = []
                register_dict[()].append(key)

        summary = ["Return registers:"]

        for regs, types in register_dict.items():
            if regs:
                if len(regs) == 1:
                    # Single register
                    summary.append(f"- {' : '.join(types)}")
                    summary.append(
                        f" - passed in registers: {', '.join([f'{reg}' for reg in regs])}"
                    )
                else:
                    # Paired registers
                    summary.append(f"- {' : '.join(types)}")
                    summary.append(
                        f" - passed in registers {pairs_order}: {', '.join([f'{reg}' for reg in regs])}"
                    )
            else:
                # No registers
                summary.append(f"- {' : '.join(types)}")
                summary.append(" - passed in registers: None")

        summary.append("")
        return "\n".join(summary)

    def run_test(self, citeration, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)
        argv = [argv]

        tmp = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers_fill"], citeration["inconsistencies"] = tmp

        tmp = hutils.find_registers_pairs(argv.copy(), register_banks)
        (
            citeration["registers_pairs"],
            citeration["inconsistencies"],
            citeration["pairs_order"],
        ) = tmp

        return citeration


class ReturnAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "return")
        self.assembly_files += ["src/arch/riscv2.s"]
        self.return_tests = ReturnTests(Target)

    def analyze_for_dtype(self, dtype):
        # Get the sizeof the current data type.
        sizeof = self.Target.get_type_details(dtype)["size"]

        # Reset the already used values.
        helper.reset_used_values()

        # Generate a single hexadecimal value.
        hvalue_return = helper.generate_hexa_value(sizeof)

        # Generate and build/execute the test case.
        stdout = self.generate(
            ReturnGenerator(self.Target, dtype).generate_single_call(
                hvalue_return
            )
        )

        # Parse the dump information.
        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout)

        # Get stack and register bank information
        stack = dump_information.get_stack()
        register_banks = dump_information.get_reg_banks()

        citeration = {}
        self.return_tests.run_test(
            citeration, stack, register_banks, hvalue_return
        )
        return citeration

    def analyze(self):
        dtypes = [
            "char",
            "short",
            "int",
            "long",
            "long long",
            "float",
            "double",
        ]

        results = {}
        for dtype in dtypes:
            results[dtype] = []
            results[dtype].append(self.analyze_for_dtype(dtype))

        return self.return_tests.generate_summary(results)
