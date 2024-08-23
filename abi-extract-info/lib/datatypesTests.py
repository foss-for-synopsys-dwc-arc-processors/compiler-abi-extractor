#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This class is responsible for generating a summary
report for the datatypes test case with each size, alignment
and signedness.

Also includes aggregators.
"""

import re

class DatatypesTests:
    def __init__(self):
        self.result = []
        self.categorizes = {
            "size": {},
            "align": {},
            "signedness": [],
            "struct size": {},
            "struct align": {},
            "union size": {},
            "union align": {}
        }


    def append(self, W):
        self.result.append(W)

    def get_result(self):
        return "\n".join(self.result)

    def pattern(self):
        return r'(\w[\w*\s]+)+:\s+signedness:\s+(\d),\s+size:\s+(\d+),\s+align:\s+(\d+)'

    def find_matches(self, content):
        return re.findall(self.pattern(), content)

    def categorize_data(self, matches):
        for data_type, signedness, size, alignment in matches:
            data_type = data_type.strip()
            size, alignment = str(size), str(alignment)

            if "struct" in data_type:
                base_type  = data_type[7:]
                key_prefix = "struct"
            elif "union" in data_type:
                base_type = data_type[6:]
                key_prefix = "union"
            else:
                base_type = data_type
                key_prefix = ""

            # Update relevant categorizes
            if key_prefix:
                self.categorizes[f"{key_prefix} size"].setdefault(size, []).append(base_type)
                self.categorizes[f"{key_prefix} align"].setdefault(alignment, []).append(base_type)
            else:
                self.categorizes["size"].setdefault(size, []).append(base_type)
                self.categorizes["align"].setdefault(alignment, []).append(base_type)
                if signedness == "1":
                    self.categorizes["signedness"].append(base_type)

    # Generate summary.
    def generate_summary(self):
        for key in ["size", "align", "signedness", "struct size", "struct align", "union size", "union align"]:
            self.append(f"{key}:")
            if key == "signedness":
                self.append(f" - {' : '.join(self.categorizes[key])}")
            else:
                for size, types in self.categorizes[key].items():
                    self.append(f" - {size}: {' : '.join(types)}")
            self.append("")

    def generate(self, content):
        matches = self.find_matches(content)
        self.categorize_data(matches)
        self.generate_summary()

        return self.get_result()

def generate(content):
    return DatatypesTests().generate(content)

if __name__ == "__main__":
    content = """
char                : signedness: 0, size: 1, align: 1
signed char         : signedness: 1, size: 1, align: 1
unsigned char       : signedness: 0, size: 1, align: 1
short               : signedness: 1, size: 2, align: 2
int                 : signedness: 1, size: 4, align: 4
long                : signedness: 1, size: 4, align: 4
long long           : signedness: 1, size: 8, align: 8
void*               : signedness: 0, size: 4, align: 4
float               : signedness: 1, size: 4, align: 4
double              : signedness: 1, size: 8, align: 8
long double         : signedness: 1, size: 16, align: 16
struct char         : signedness: 0, size: 1, align: 1
struct signed_char  : signedness: 0, size: 1, align: 1
struct unsigned_char: signedness: 0, size: 1, align: 1
struct short        : signedness: 0, size: 2, align: 2
struct int          : signedness: 0, size: 4, align: 4
struct long         : signedness: 0, size: 4, align: 4
struct long_long    : signedness: 0, size: 8, align: 8
struct void         : signedness: 0, size: 4, align: 4
struct float        : signedness: 0, size: 4, align: 4
struct double       : signedness: 0, size: 8, align: 8
struct long_double  : signedness: 0, size: 16, align: 16
union char          : signedness: 0, size: 1, align: 1
union signed_char   : signedness: 0, size: 1, align: 1
union unsigned_char : signedness: 0, size: 1, align: 1
union short         : signedness: 0, size: 2, align: 2
union int           : signedness: 0, size: 4, align: 4
union long          : signedness: 0, size: 4, align: 4
union long_long     : signedness: 0, size: 8, align: 8
union void          : signedness: 0, size: 4, align: 4
union float         : signedness: 0, size: 4, align: 4
union double        : signedness: 0, size: 8, align: 8
union long_double   : signedness: 0, size: 16, align: 16
"""
    content = generate(content)
    print(content)