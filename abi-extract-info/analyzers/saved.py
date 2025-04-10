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
The purpose of this generator is to create a test case to
determinate which registers are calee-saved and which are
caller-saved.

First, we reset the registers to a known value. Then, we call an
auxiliary function that will clobber all possible registers. This
tells the compiler that every register might be used or modified,
prompting the compiler to save their values. After this, we assign
different values to the registers.

Finally, we dump the register values to observe which registers
hold which values. Callee-saved registers should retain the second
set of values we assigned.

For caller-saved registers, we expect them to hold the first set of values.
This process may need further refinement.
"""


class ReturnGenerator:
    def __init__(self, Target):
        self._result = []
        self.Target = Target

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_prototypes_aux(self):
        self.append("extern void set_registers (int);")
        self.append("int dummy;")

    def generate_prototypes_main(self):
        self.append("extern void callee (void);")
        self.append("extern void set_registers (int);")
        self.append("#define dump callee // this is temporary.")
        self.append("int* aux (void);")

    def generate_func_aux(self, hvalue_callee_saved):

        register_names = []
        for value in self.Target.get_registers().values():
            register_names.extend(value)

        register_names_str = '", "'.join(register_names)
        register_names_str = f'"{register_names_str}"'

        self.append(
            """
void aux (void) {
    asm volatile (""
    :
    :
    : %s);

    set_registers(%s);

    /* Preventing the compiler from optimizing. */
    asm volatile("":::);
}
"""
            % (register_names_str, hvalue_callee_saved)
        )

    def generate_func_main(self, hvalue_caller_saved):
        self.append(
            """
int main (void) {
    set_registers(%s);
    aux();
    dump();

    return 0;
}
"""
            % (hvalue_caller_saved)
        )

    def generate_main(self, hvalue_caller_saved):
        self.generate_prototypes_main()
        self.generate_func_main(hvalue_caller_saved)

        return self.get_result()

    def generate_aux(self, hvalue_callee_saved):
        self.generate_prototypes_aux()
        self.generate_func_aux(hvalue_callee_saved)

        return self.get_result()


class SavedTests:
    def __init__(self, Target):
        self.Target = Target

    def generate_summary(self, caller, callee):

        caller_str = ", ".join(caller)
        callee_str = ", ".join(callee)

        summary = []
        summary.append("Caller/callee-saved test:")
        summary.append(f" - caller-saved {caller_str}")
        summary.append(f" - callee-saved {callee_str}")
        summary.append("")

        return "\n".join(summary)

    def run_test(
        self, register_banks, hvalue_caller_saved, hvalue_callee_saved
    ):
        hutils = hexUtils.HexUtils(self.Target)

        tmp = hutils.find_registers_fill([hvalue_caller_saved], register_banks)
        caller_saved_registers, _ = tmp

        tmp = hutils.find_registers_fill([hvalue_callee_saved], register_banks)
        callee_saved_registers, _ = tmp

        return self.generate_summary(
            caller_saved_registers, callee_saved_registers
        )


class SavedAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "saved")

    def analyze(self):
        sizeof = self.Target.get_type_details("int")["size"]

        # Generate value for callee/caller saved registers.
        helper.reset_used_values()
        hvalue_caller_saved = helper.generate_hexa_value(sizeof)
        hvalue_callee_saved = helper.generate_hexa_value(sizeof)

        stdout = self.generate(
            [
                ReturnGenerator(self.Target).generate_main(hvalue_caller_saved),
                ReturnGenerator(self.Target).generate_aux(hvalue_callee_saved),
            ]
        )

        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout)
        register_banks = dump_information.get_reg_banks()

        return SavedTests(self.Target).run_test(
            register_banks, hvalue_caller_saved, hvalue_callee_saved
        )
