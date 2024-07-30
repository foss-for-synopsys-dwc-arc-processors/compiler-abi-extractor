#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

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

from lib import helper

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
        self.append("""
inline static double ull_as_double(unsigned long long lhs) {
    double result;
    memcpy(&result, &lhs, sizeof(result));
    return result;
}
""")

    def generate_as_float(self):
        self.append("""
inline static float int_as_float(unsigned int lhs) {
    float result;
    memcpy(&result, &lhs, sizeof(result));
    return result;
}
""")

    def generate_converter(self, datatype):
        if datatype == "double":
            self.generate_include()
            self.generate_as_double()
        elif datatype == "float":
            self.generate_include()
            self.generate_as_float()

    def generate_main(self, datatype, values_list):
        types_list = [datatype] * len(values_list)
        types_str = ", ".join(types_list)

        if datatype == "double":
            values_str = ", ".join(f"ull_as_double({value})" for value in values_list)
        elif datatype == "float":
            values_str = ", ".join(f"int_as_float({value})" for value in values_list)
        else:
            values_str = ", ".join(values_list)

        self.append("""
extern void callee(%s);

int main(void) {
    callee(%s);
}
""" % (types_str, values_str))

    def generate(self, datatype, values_list):
        self.generate_converter(datatype)
        self.generate_main(datatype, values_list)

        return self.get_result()

# Function to initiate the generation process
def generate(Target, datatype, count):
    return ArgPassGenerator(Target).generate(datatype, count)

import sys
if __name__ == "__main__":
    # Generating the files content
    datatype = "int"
    count = 8
    content = generate(datatype, count)
    open(f"{datatype}.c", "w").write(content)
