#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""
This class parses the bit-field test case to a summary.
It validates how bit-fields are mapped in memory.
"""

class BitFieldTests:
    def __init__(self):
        self.results = []

    def append(self, W):
        self.results.append(W)

    def get_results(self):
        return "\n".join(self.results)

    def process_results(self, content):
        lines = content.split("\n")
        types = []

        for l in lines:
            if not l:
                continue

            dtype, sign, padding, endian = l.split(":")

            found = False
            for index, j in enumerate(types.copy()):
                if j["sign"] == sign and j["padding"] == padding and j["endian"] == endian:
                    types[index]["dtypes"].append(dtype)
                    found = True

            # This has been optimized. It used to be in the beginning of the loop and at the end.
            # But if the types array is empty, it will not enter the loop and enter here anyway.
            if not found:
                types.append( {"dtypes": [dtype], "sign": sign, "padding": padding, "endian": endian} )
                continue

        # Collect unique endians
        endians = {e["endian"] for e in types}

        return types, endians

    def summary_results(self, types, endians):
        # TODO: If different datatypes have different memory layouts,
        # it will be ignored (yet).
        self.append("Bit-Field test:")
        for t in types:
            self.append(f"- sum(bit-fields) {t['sign']} sizeof(dtype)")
            self.append(f"  - {t['padding']}")
            if len(endians) > 1:
                self.append(f"  - {t['endian']}")

        if len(endians) == 1:
            self.append(f"- {''.join(endians)}")


    def prepare_summary(self, content):
        types, endians = self.process_results(content)
        self.summary_results(types, endians)
        return self.get_results()


def prepare_summary(content):
    return BitFieldTests().prepare_summary(content)

if __name__ == "__main__":
    content = """short:>:Extra padding.:Little endian.
short:<:No extra padding.:Little endian.
int:>:Extra padding.:Little endian.
int:<:No extra padding.:Little endian."""

    content = prepare_summary(content)
    print(content)
