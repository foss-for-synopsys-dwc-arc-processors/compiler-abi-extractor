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
        declare_str = [f"char a{c};" for c in range(self._count)]
        declare_str.append(f"char a{self._count};")
        declare_str = "\n".join(declare_str)
        self.append("""
struct structType {
%s
};
""" % (declare_str))

    def generate_single_call_prototypes(self):
        self.append("extern void callee(struct structType);")
        self.append("extern void reset_registers();")

    def generate_single_call_main(self):
        dtypes = [self._dtype] * self._count + ["char"]
        argv = helper.generate_hexa_list_from_datatypes(dtypes, self.Target, self._count)
        self.append("""
int main (void) {
    reset_registers();
    struct structType structTypeObject = { %s };
    callee(structTypeObject);
}
""" % (", ".join(argv)))

    def generate_single_call(self):
        self.generate_single_call_declare()
        self.generate_single_call_prototypes()
        self.generate_single_call_main()

        return self.get_result()


    def generate_multiple_call_declare(self):
        for c in range(self._count + 1):
            declare_str = [f"{self._dtype} a{j};" for j in range(c+1)]
            if c == self._count:
                declare_str.append(f"char a{self._count + 1};")

            declare_str = "\n".join(declare_str)
            self.append("""
struct structType%d {
%s
};
""" % (c, declare_str))

    def generate_multiple_call_prototypes(self):
        self.append("extern void callee();")
        self.append("extern void reset_registers(void);")

    def generate_multiple_call_main(self):
        self.append("int main (void) {")
        for c in range(self._count + 1): # +1 for the extra char call.
            dtypes = [self._dtype] * (c+1)
            reset = 10 if c == 0 else None
            argv   = helper.generate_hexa_list_from_datatypes(dtypes, self.Target, reset)

            if self._dtype == "float":
                argv = [f"ul_as_float({x})" for x in argv]
            elif self._dtype == "double":
                argv = [f"ull_as_double({x})" for x in argv]

            if c == self._count:
                sizeof_char = self.Target.get_type_details("char")["size"]
                char_value = helper.generate_hexa_values_2(sizeof_char)
                argv_str = f"{', '.join(argv)}, {char_value}"
            else:
                argv_str = ", ".join(argv)

            self.append("""
    reset_registers();
    struct structType%d structTypeObject%d = { %s };
    callee(structTypeObject%d);
""" % (c, c, argv_str, c))

        self.append("}")

    def generate_multiple_call(self):
        self.generate_converter()

        self.generate_multiple_call_declare()
        self.generate_multiple_call_prototypes()
        self.generate_multiple_call_main()

        return self.get_result()

def generate_single_call(Target, count, dtype, sizeof):
    return StructGenerator(Target, count, dtype, sizeof).generate_single_call()

def generate_multiple_call(Target, count, dtype, sizeof):
    return StructGenerator(Target, count, dtype, sizeof).generate_multiple_call()

import sys
if __name__ == "__main__":
    pass
