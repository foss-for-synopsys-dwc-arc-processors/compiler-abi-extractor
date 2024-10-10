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

    # e.g
    # [{'dtype': ['short'], 'sign': '>', 'content': ['', '',
    #                                                'No extra padding.:Little-endian.Extra padding.:Little-endian.']},
    #  {'dtype': ['short'], 'sign': '<', 'content': ['No extra padding.:Little-endian.',
    #                                                'No extra padding.:Little-endian.',
    #                                                'No extra padding.:Little-endian.']},
    #  {'dtype': ['int'], 'sign': '>', 'content': ['Extra padding.:Little-endian.',
    #                                              'Extra padding.:Little-endian.',
    #                                              'Extra padding.:Little-endian.']},
    #  {'dtype': ['int'], 'sign': '<', 'content': ['No extra padding.:Little-endian.',
    #                                              'No extra padding.:Little-endian.',
    #                                              'No extra padding.:Little-endian.']},
    #  ...
    def process_stage1(self, content):
        # Split the input content into individual entries
        data = content.split("\n")

        entries = []
        for entry in data:
            if not entry:
                continue

            # Split the string to get dtype, sign, and content
            sdata   = entry.split(":")
            dtype   = sdata[0][:-2]  # Removing the '_0', '_1', etc. from dtype
            sign    = sdata[1]
            content = ":".join(sdata[2:])

            found = False
            for e in entries:
                if e["dtype"][0] == dtype and e["sign"] == sign:
                    e["content"].append(content)  # Append content to existing entry
                    found = True
                    break

            if not found:
                entries.append({ "dtype": [dtype], "sign": sign, "content": [content] })

        return entries

    # e.g
    # [{'dtype': ['short'], 'sign': '>', 'content': 'unknown'},
    #  {'dtype': ['short'], 'sign': '<', 'content': 'No extra padding.:Little-endian.'},
    #  {'dtype': ['int'], 'sign': '>', 'content': 'Extra padding.:Little-endian.'},
    #  {'dtype': ['int'], 'sign': '<', 'content': 'No extra padding.:Little-endian.'}
    #  ...
    def process_stage2(self, entries):
        # Find the most frequent content for each entry
        for entry in entries:
            occurrences = {}

            # Count occurrences of each content
            for c in entry["content"]:
                if c in occurrences:
                    occurrences[c] += 1
                else:
                    occurrences[c] = 1

            # Get the most frequent content (or 'unknown' if no clear winner)
            max_entry = max(occurrences, key=occurrences.get)
            entry["content"] = max_entry or "unknown"

        return entries

    # e.g
    # [{'dtype': ['short'], 'sign': '>', 'content': 'unknown'},
    #  {'dtype': ['short', 'int', 'long', 'long_long'], 'sign': '<', 'content': 'No extra padding.:Little-endian.'},
    #  {'dtype': ['int', 'long', 'long_long'], 'sign': '>', 'content': 'Extra padding.:Little-endian.'}]
    def process_stage3(self, entries):
        # Merge entries based on sign and content
        for entry in entries:
            for entry2 in entries.copy():
                if entry["dtype"] == entry2["dtype"]:
                    continue

                # If sign and content are the same, merge dtype
                if entry["sign"] == entry2["sign"] and entry["content"] == entry2["content"]:
                    entry["dtype"].extend(entry2["dtype"])
                    entries.remove(entry2)  # Remove merged entry

        return entries

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

    def summary_results(self, entries):
        self.append("Bit-Field test:")
        for sign in [">", "<"]:
            self.append(f"- sum(bit-fields) {sign} sizeof(datatype)")
            for entry in entries:
                if entry["sign"] == sign:
                    self.append(f"  - {' : '.join(entry['dtype'])}")
                    tmp = entry["content"].replace(":", "\n    - ")
                    self.append(f"    - {tmp}")

    def prepare_summary(self, content):
        entries = self.process_stage1(content)
        entries = self.process_stage2(entries)
        entries = self.process_stage3(entries)
        self.summary_results(entries)
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
