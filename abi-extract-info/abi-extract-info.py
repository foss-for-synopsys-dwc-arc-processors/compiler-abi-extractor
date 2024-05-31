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


def do_datatypes(Driver, Report):
    Content = datatypesTests.generate()
    open("tmp/out_datatypes.c", "w").write(Content)
    Driver.compile("tmp/out_datatypes.c", "tmp/out_datatypes.s")
    Driver.assemble("tmp/out_datatypes.s", "tmp/out_datatypes.o")
    Driver.link("tmp/out_datatypes.o", "tmp/out_datatypes.elf")
    Driver.simulate("", "tmp/out_datatypes.elf", "tmp/out_datatypes.txt")

    # Store the generated report file for datatypes test case.
    Report.append("tmp/out_datatypes.txt")

def do_argpass(Driver, Report):
    Driver.compile("src/argpass/caller.c", "tmp/out_caller.s")
    Driver.assemble("tmp/out_caller.s", "tmp/out_caller.o")
    Driver.assemble("src/argpass/riscv/callee.s", "tmp/out_callee.o")
    Driver.link(["tmp/out_callee.o", "tmp/out_caller.o"], "tmp/out_argpass.elf")
    Driver.simulate("", "tmp/out_argpass.elf", "tmp/out_argpass.stdout")
    Content = argPassTests.parser("tmp/out_argpass.stdout")
    open("tmp/out_argpass.txt", "w").write("".join(Content))

    # Store the generated report file for argument passing test case.
    Report.append("tmp/out_argpass.txt")

def do_endianness(Driver, Report):
    Driver.compile("src/endianness/endianness.c", "tmp/out_endianness.s")
    Driver.assemble("tmp/out_endianness.s", "tmp/out_endianness.o")
    Driver.link("tmp/out_endianness.o", "tmp/out_endianness.elf")
    Driver.simulate("", "tmp/out_endianness.elf", "tmp/out_endianness.stdout")

    Report.append("tmp/out_endianness.stdout")

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
