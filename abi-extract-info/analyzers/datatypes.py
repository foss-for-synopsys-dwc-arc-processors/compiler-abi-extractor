# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import re

import analyzer
import helper

Types = [
    "char",
    "signed char",
    "unsigned char",
    "short",
    "int",
    "long",
    "long long",
    "void*",
    "float",
    "double",
    "long double",
]


class DataTypesGenerator:
    def __init__(self):
        self.Result = []
        self.Globals = []

    def append(self, W):
        self.Result.append(W)

    def generateBase(self):
        self.append(
            """
#include <stdio.h>
#include <stdint.h>

void print_info(const char *datatype, int signedness, size_t size, uintptr_t theOffset) {
   printf("%-20s: signedness: %d, size: %zu, align: %zu\\n", datatype, signedness, size, (size_t)theOffset);
}

"""
        )

    # Generate global variabels for each type and print runtime information about them
    def generateTypeChecksUsingStructs(self):

        # Generate Structs  for each type and print runtime information about them
        for I, T in enumerate(Types):
            self.append(
                """struct struct_%s {
  %s theType;
};"""
                % (T.replace(" ", "_").replace("*", ""), T)
            )

            self.append(
                """struct StructType%d {
  char dummy;
  struct struct_%s theType;
} theStructTypeObject%d;
"""
                % (I, T.replace(" ", "_").replace("*", ""), I)
            )

        # Generate Unions for each type and print runtime information about them
        for I, T in enumerate(Types):
            self.append(
                """union union_%s {
  char dummy;
  %s theType;
};"""
                % (T.replace(" ", "_").replace("*", ""), T)
            )

            self.append(
                """struct UnionType%d {
  char dummy;
  union union_%s theType;
} theUnionTypeObject%d;
"""
                % (I, T.replace(" ", "_").replace("*", ""), I)
            )

        for I, T in enumerate(Types):
            # Ensure we always start with an odd address (as far as C standard guarantees this)
            self.append(
                """struct Type%d {
  char dummy;
  %s theType;
} theTypeObject%d;
"""
                % (I, T, I)
            )

        self.append("void analyzeTypesUsingGlobals() {")
        for I, T in enumerate(Types):
            # Omitting the assignment of "-1" to "void*" because some compilers consider it an error.
            if T != "void*":
                self.append(f"  theTypeObject{I}.theType = -1;")
                self.append(
                    f'  print_info("{T}", theTypeObject{I}.theType == -1, sizeof({T}), (uintptr_t)&theTypeObject{I}.theType-(uintptr_t)&theTypeObject{I}.dummy);'
                )
            else:
                self.append(
                    f'  print_info("{T}", 0, sizeof({T}), (uintptr_t)&theTypeObject{I}.theType-(uintptr_t)&theTypeObject{I}.dummy);'
                )

        for I, T in enumerate(Types):
            Struct = T.replace(" ", "_").replace("*", "")
            self.append(
                f'  print_info("struct {Struct}", 0, sizeof(struct struct_{Struct}), (uintptr_t)&theStructTypeObject{I}.theType-(uintptr_t)&theStructTypeObject{I}.dummy);'
            )

        for I, T in enumerate(Types):
            Union = T.replace(" ", "_").replace("*", "")
            self.append(
                f'  print_info("union {Union}", 0, sizeof(union union_{Union}), (uintptr_t)&theUnionTypeObject{I}.theType-(uintptr_t)&theUnionTypeObject{I}.dummy);'
            )

        self.append("}\n")

    def generateMain(self):
        self.append(
            """
int main() {
  analyzeTypesUsingGlobals();
}
"""
        )

    def getResult(self):
        return "\n".join(self.Result)

    def generate(self):
        self.generateBase()
        self.generateTypeChecksUsingStructs()
        self.generateMain()

        return self.getResult()


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
            "union align": {},
        }

    def append(self, W):
        self.result.append(W)

    def get_result(self):
        return "\n".join(self.result)

    def pattern(self):
        return r"(\w[\w*\s]+)+:\s+signedness:\s+(\d),\s+size:\s+(\d+),\s+align:\s+(\d+)"

    def find_matches(self, content):
        return re.findall(self.pattern(), content)

    def categorize_data(self, matches):
        for data_type, signedness, size, alignment in matches:
            data_type = data_type.strip()
            size, alignment = str(size), str(alignment)

            if "struct" in data_type:
                base_type = data_type[7:]
                key_prefix = "struct"
            elif "union" in data_type:
                base_type = data_type[6:]
                key_prefix = "union"
            else:
                base_type = data_type
                key_prefix = ""

            # Update relevant categorizes
            if key_prefix:
                self.categorizes[f"{key_prefix} size"].setdefault(
                    size, []
                ).append(base_type)
                self.categorizes[f"{key_prefix} align"].setdefault(
                    alignment, []
                ).append(base_type)
            else:
                self.categorizes["size"].setdefault(size, []).append(base_type)
                self.categorizes["align"].setdefault(alignment, []).append(
                    base_type
                )
                if signedness == "1":
                    self.categorizes["signedness"].append(base_type)

    # Generate summary.
    def generate_summary(self):
        for key in [
            "size",
            "align",
            "signedness",
            "struct size",
            "struct align",
            "union size",
            "union align",
        ]:
            self.append(f"Datatype {key} test:")
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


class DataTypesAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "datatypes")

    def analyze(self):
        Stdout = self.generate(DataTypesGenerator().generate())
        self.Target.set_type_details(helper.parse_type_info(Stdout))
        return DatatypesTests().generate(Stdout)
