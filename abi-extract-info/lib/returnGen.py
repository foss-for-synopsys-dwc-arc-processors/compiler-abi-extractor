#!/bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import helper

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
    def __init__(self, Target, count, dtype, sizeof):
        self._result = []
        self.Target = Target
        self._count = count
        self._dtype = dtype
        self._sizeof = sizeof

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_include(self):
        self.append("#include <string.h>")

    def generate_as_float(self):
        self.append("""
inline static float ul_as_float(unsigned long lhs)
{
    float result;
    memcpy(&result, &lhs, sizeof(float));
    return result;
}
""")

    def generate_as_double(self):
        self.append("""
inline static double ull_as_double(unsigned long long lhs)
{
    double result;
    memcpy(&result, &lhs, sizeof(double));
    return result;
}
""")

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
        self.append("extern void reset_registers (void);")

    def generate_single_call_bar(self):
        argv = helper.generate_hexa_values_2(self._sizeof, 20)
        if self._dtype == "float":
            argv = f"ul_as_float({argv})"
        elif self._dtype == "double":
            argv = f"ull_as_double({argv})"

        self.append("""
%s bar (void) {
    /* %s a = %s; */
    reset_registers();
    return %s;
}
""" % (self._dtype, self._dtype, argv, argv))

    def generate_single_call_main(self):
        self.append("""
int main (void) {
    foo ();
    return 0;
}
""")

    def generate_single_call(self):
        self.generate_converter()

        self.generate_single_call_prototypes()
        self.generate_single_call_bar()
        self.generate_single_call_main()

        return self.get_result()

def generate_single_call(Target, count, dtype, sizeof):
    return ReturnGenerator(Target, count, dtype, sizeof).generate_single_call()

if __name__ == "__main__":
    content = generate_single_call(None, None, 'int', 4)
    print(content)
