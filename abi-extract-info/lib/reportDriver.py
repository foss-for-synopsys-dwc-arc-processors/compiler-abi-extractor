#!/bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

"""

This driver serves the purpose of consolidating all generated
test results into a single summary report file upon the conclusion
of the `abi-extract-info` tool.
"""

class ReportDriver:
    def __init__(self):
        self.Files = []
        self.ReportFile = "report.txt"

    def append(self, W):
        self.Files.append(W)

    def readFile(self, filePath):
        with open(filePath, "r") as file:
            content = file.read()
        return content

    def generateReport(self):
        with open(self.ReportFile, "w") as outFile:
            for filePath in self.Files:
                content = self.readFile(filePath)
                outFile.writelines(content + "\n")

import sys
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 reportDriver.py <file_name01>,<file_name02>,..")
        sys.exit(1)
    Driver = ReportDriver()
    for f in sys.argv[1].split(","):
        Driver.append(f)

    Driver.generateReport()
