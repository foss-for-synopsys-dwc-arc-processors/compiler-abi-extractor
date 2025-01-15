#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import helper

"""
The purpose of this generator is to create a C test case that validates the
struct size boundaries during argument passing before being passed by
reference on the stack.

Given a list of data types, it generates a struct that is passed to an
external `callee()` function, which is responsible for dumping the register
and stack values.
"""

class StructGenerator:
    def __init__(self, Target, count, dtypes):
        self._result = []
        self.Target = Target
        self._count = count
        self.dtypes = dtypes

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_include(self):
        self.append("#include <stdio.h>")
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
        if "float" in self.dtypes:
            self.generate_as_float()
        if "double" in self.dtypes:
            self.generate_as_double()

    def generate_single_call_declare(self):
        declare_str = [f"    {dtype} a{i + 1};" for i, dtype in enumerate(self.dtypes)]
        declare_str = "\n".join(declare_str)
        self.append("""
struct structType {
%s
};
""" % (declare_str))

    def generate_single_call_prototypes(self):
        self.append("extern void callee(struct structType);")
        self.append("extern void reset_registers();")

    def generate_single_call_main(self, hvalues):
        hvalues_str = []
        for index, dtype in enumerate(self.dtypes):
            if dtype == "float":
                hvalues_str.append(f"ul_as_float({hvalues[index]})")
            elif dtype == "double":
                hvalues_str.append(f"ull_as_double({hvalues[index]})")
            else:
                hvalues_str.append(hvalues[index])
        self.append("""
int main (void) {
    printf("Sizeof(struct structType): %%d\\n", sizeof(struct structType));
    reset_registers();
    struct structType structTypeObject = { %s };
    callee(structTypeObject);

    return 0;
}
""" % (", ".join(hvalues_str)))

    def generate_single_call(self, hvalues):
        self.generate_include()
        self.generate_converter()
        self.generate_single_call_declare()
        self.generate_single_call_prototypes()
        self.generate_single_call_main(hvalues)

        return self.get_result()

def generate_single_call(Target, count, dtypes, hvalues):
    return StructGenerator(Target, count, dtypes).generate_single_call(hvalues)

import sys
if __name__ == "__main__":
    pass
