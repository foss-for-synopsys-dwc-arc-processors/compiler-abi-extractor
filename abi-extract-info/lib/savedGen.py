#!/bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import helper

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
    def __init__(self, Target, sizeof):
        self._result = []
        self.Target = Target
        self._sizeof = sizeof

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_prototypes(self):
        self.append("extern void callee (void);")
        self.append("extern void reset_registers (void);")
        self.append("extern void set_registers (int);")
        self.append("#define dump callee // this is temporary.")

    def generate_foobar(self):
        argv = helper.generate_hexa_values_2(self._sizeof, 30)
        register_names = self.Target.get_registers()
        register_names_str = '", "'.join(register_names)
        register_names_str = f'"{register_names_str}"'

        self.append("""
void aux (void) {
    asm volatile (""
    :
    :
    : %s);

    set_registers(%s);
}
""" % (register_names_str, argv))

    def generate_main(self):
        argv = helper.generate_hexa_values_2(self._sizeof)
        self.append("""
int main (void) {
    reset_registers();
    set_registers(%s);
    aux();
    dump();

    return 0;
}
""" % (argv))

    def generate(self):
        self.generate_prototypes()
        self.generate_foobar()
        self.generate_main()

        return self.get_result()

def generate(Target, sizeof):
    return ReturnGenerator(Target, sizeof).generate()

if __name__ == "__main__":
    content = generate(None, None, 'int', 4)
    print(content)
