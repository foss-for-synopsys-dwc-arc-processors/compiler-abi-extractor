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
    def __init__(self, ReportFile, OptionParser):
        self.Files = []
        self.ReportFile = ReportFile
        self.OptionParser = OptionParser

    def append(self, W):
        self.Files.append(W)

    def readFile(self, filePath):
        with open(filePath, "r") as file:
            content = file.read()
        return content

    def generateReport(self, reportFile=None):
        # By default the report file output is defined
        # in the class constructor, althought for testing
        # purposes the output file path needs to be altered
        # through command-line execution.
        if reportFile is None:
            reportFile = self.ReportFile
        with open(reportFile, "w") as outFile:
            for filePath in self.Files:
                content = self.readFile(filePath)
                outFile.writelines(content + "\n")

        print(f"Report file generated at {reportFile}")
        if self.OptionParser.get("print-report"):
            print(self.readFile(reportFile))


import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python3 reportDriver.py <file_name01>,<file_name02>,.. [output_file]"
        )
        sys.exit(1)
    Driver = ReportDriver()
    for f in sys.argv[1].split(","):
        Driver.append(f)

    reportFile = None
    if len(sys.argv) > 2:
        reportFile = sys.argv[2]
    Driver.generateReport(reportFile)
