#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import compilationDriver
from lib import reportDriver
from lib import datatypesTests
from lib import argPassTests
from lib import argPassTestsGen

def do_datatypes(Driver, Report):
    Content = datatypesTests.generate()
    open("tmp/out_datatypes.c", "w").write(Content)
    stdoutFile = Driver.run(["tmp/out_datatypes.c"], [], "out_datatypes")

    # Store the generated report file for datatypes test case.
    Report.append(stdoutFile)

def do_argpass(Driver, Report):
    Content = argPassTestsGen.generate()

    OutputContent = argPassTests.header()
    for type_name, content in Content:
        type_name_replaced = type_name.replace(' ','_')

        SrcFile = f"tmp/out_caller_{type_name_replaced}.c"
        open(SrcFile, "w").write(content)
        StdoutFile = Driver.run([SrcFile], ["src/argpass/riscv/callee.s"], f"out_argpass_{type_name_replaced}")
        OutputContent += argPassTests.parser(StdoutFile, type_name)

    ParsedFile = f"tmp/out_argpass.txt"
    open(ParsedFile, "w").write("".join(OutputContent))

    # Store the generated report file for argument passing test case.
    Report.append(ParsedFile)


def do_endianness(Driver, Report):
    stdoutFile = Driver.run(["src/endianness/endianness.c"], [], "out_endianness")
    Report.append(stdoutFile)

def do_tests(Driver, Report):
     do_datatypes(Driver, Report)
     do_argpass(Driver, Report)
     do_endianness(Driver, Report)
     # ,, more different kind of tests here

if __name__ == "__main__":
    Driver = compilationDriver.CompilationDriver()
    Report = reportDriver.ReportDriver()
    do_tests(Driver, Report)

    # Generate summary report.
    Report.generateReport()
