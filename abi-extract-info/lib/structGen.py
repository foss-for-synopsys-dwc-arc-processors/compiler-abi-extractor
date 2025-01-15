#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import helper

"""
The purpose of this generator is to create a test case
that will validate the boundaries before a struct with
values goes to the stack.

For a given datatype, will generate single or multiple
structs being passed to an extern callee() function
responsible for dumping the registger and stack values.
"""

class StructGenerator:
    def __init__(self, Target, count, dtype):
        self._result = []
        self.Target = Target
        self._count = count
        self._dtype = dtype

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
        declare_str = [f"char a{c};" for c in range(1, self._count + 1)]
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
        dtypes = [self._dtype] * self._count + ["char"]
        self.append("""
int main (void) {
    printf("Sizeof(struct structType): %%d\\n", sizeof(struct structType));
    reset_registers();
    struct structType structTypeObject = { %s };
    callee(structTypeObject);
}
""" % (", ".join(hvalues)))

    def generate_single_call(self, hvalues):
        self.generate_single_call_declare()
        self.generate_single_call_prototypes()
        self.generate_single_call_main(hvalues)

        return self.get_result()

    def generate_multiple_call_declare(self, argument_data):
        for c in range(1, self._count + 1):
            dtypes = argument_data[c]["dtypes"]
            declare_str = [f"{dtype} a{index};" for index, dtype in enumerate(dtypes)]
            declare_str = "\n".join(declare_str)
            self.append("""
struct structType%d {
%s
};
""" % (c, declare_str))

    def generate_multiple_call_prototypes(self):
        self.append("extern void callee();")
        self.append("extern void reset_registers(void);")

    def generate_multiple_call_main(self, argument_data):
        self.append("int main (void) {")
        for c in range(1, self._count + 1):
            argv     = []
            dtypes_  = argument_data[c]["dtypes"]
            hvalues_ =  argument_data[c]["hvalues"]
            for dtype, hvalue in zip(dtypes_, hvalues_):
                if dtype == "float":
                    argv.append(f"ul_as_float({hvalue})")
                elif dtype == "double":
                    argv.append(f"ull_as_double({hvalue})")
                else:
                    argv.append(hvalue)
            argv_str = ", ".join(argv)

            self.append("""
    reset_registers();
    struct structType%d structTypeObject%d = { %s };
    callee(structTypeObject%d);
""" % (c, c, argv_str, c))

        self.append("}")

    def generate_multiple_call(self, argument_data):
        self.generate_converter()

        self.generate_multiple_call_declare(argument_data)
        self.generate_multiple_call_prototypes()
        self.generate_multiple_call_main(argument_data)

        return self.get_result()

def generate_single_call(Target, count, dtype, hvalues):
    return StructGenerator(Target, count, dtype).generate_single_call(hvalues)

def generate_multiple_call(Target, count, dtype, argument_data):
    return StructGenerator(Target, count, dtype).generate_multiple_call(argument_data)

import sys
if __name__ == "__main__":
    pass
