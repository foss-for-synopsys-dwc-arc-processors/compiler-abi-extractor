#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import compilationDriver
from lib import reportDriver
from lib import datatypesTests
from lib import stackAlignTests
from lib import argPassTests
from lib import argPassTestsGen
from lib import optionParser
from lib import helper

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
        StdoutFile = Driver.run([SrcFile], ["src/arch/riscv.s"], f"out_argpass_{type_name_replaced}")
        OutputContent += argPassTests.parser(StdoutFile, type_name)

    ParsedFile = f"tmp/out_argpass.txt"
    open(ParsedFile, "w").write("".join(OutputContent))

    # Store the generated report file for argument passing test case.
    Report.append(ParsedFile)


def do_endianness(Driver, Report):
    stdoutFile = Driver.run(["src/endianness/endianness.c"], [], "out_endianness")
    Report.append(stdoutFile)

def do_stack_dir(Driver, Report):
    stdoutFile = Driver.run(["src/stack_dir/main.c", "src/stack_dir/A.c", "src/stack_dir/B.c"], [], "out_stackdir")
    Report.append(stdoutFile)

def do_stack_align(Driver, Report):
    Content = stackAlignTests.generateDriver()
    open("tmp/out_driver.c", "w").write(Content)
    Content = stackAlignTests.generateFunctions()
    open("tmp/out_functions.c", "w").write(Content)
    Content = stackAlignTests.generateFunctionsHeader()
    open("tmp/out_functions.h", "w").write(Content)

    stdoutFile = Driver.run(["tmp/out_functions.c", "tmp/out_driver.c"], ["src/arch/riscv.s"], "out_stackalign")
    Report.append(stdoutFile)

def do_tests(Driver, Report):
     do_datatypes(Driver, Report)
     do_argpass(Driver, Report)
     do_endianness(Driver, Report)
     do_stack_dir(Driver, Report)
     do_stack_align(Driver, Report)
     # ,, more different kind of tests here

if __name__ == "__main__":
    # Parse options
    OptionParser = optionParser.OptionParser().instance()
    OptionParser.option_parser()

    # Construct the report name from options
    cc_option  = OptionParser.get('cc')
    sim_option = OptionParser.get('sim')
    ReportName = f"{cc_option}_{sim_option}.report"

    # Set environment variable
    helper.set_env(cc_option, sim_option)

    # Initialize the report driver with the report name
    Report = reportDriver.ReportDriver(ReportName, OptionParser)

    print(f"Running {cc_option} with {sim_option}...")

    is_verbose = OptionParser.get('verbose')
    Driver = compilationDriver.CompilationDriver(is_verbose)

    # Run tests and generate summary report
    do_tests(Driver, Report)
    Report.generateReport()
