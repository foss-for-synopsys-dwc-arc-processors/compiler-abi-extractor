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
from lib import argPassTestsGenStructs
from lib import optionParser
from lib import helper

from lib import emptyStructGen
from lib import emptyStructTests
from lib import dumpInformation
from lib import targetArch
from lib import structGen
from lib import structTests

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

def do_argpass_struct(Driver, Report):
    Content = argPassTestsGenStructs.generate()

    OutputContent = argPassTests.header()
    for type_name, content in Content:
        type_name_replaced = type_name.replace(' ','_')

        if type_name_replaced != "double":
            continue

        SrcFile = f"tmp/out_caller_{type_name_replaced}.c"
        open(SrcFile, "w").write(content)
        StdoutFile = Driver.run([SrcFile, "src/helper.c"], ["src/arch/riscv.s"], f"out_argpass_{type_name_replaced}")
        OutputContent += argPassTests.parser(StdoutFile, type_name)

    ParsedFile = f"tmp/out_argpass.txt"
    open(ParsedFile, "w").write("".join(OutputContent))

    # Store the generated report file for argument passing test case.
    Report.append(ParsedFile)


def do_empty_struct(Driver, Report, Target):
    # This value is to be defined according to number for
    # argument passing in registers from "do_argpass" test case.
    MaxCallCount = 8 # Current static value. FIXME
    Content = emptyStructGen.generate(MaxCallCount)
    open("tmp/out_emptyStruct.c", "w").write(Content)

    StdoutFile = Driver.run(["tmp/out_emptyStruct.c", "src/helper.c"], ["src/arch/riscv.s"], "out_emptyStruct")
    emptyStructTests.split_sections(StdoutFile, Target)

def do_struct_boundaries(Driver, Report, Target):
    types = ["char", "int", "double"]

    # This value is to be defined according to the sizeof(int) (XLEN).
    # According to the RISCV ABI document, the limits are 2 * XLEN
    # 2 * XLEN; (XLEN==sizeof(int)) Hardcoded to 4. FIXME
    # OR this logic is to be changed as the "max_boundary" value must be defined
    # the first char iteration (?).
    max_boundary = 2*4
    boundary_limit_count = 0
    for dataType in types:
        if dataType == "char":
            datatype_size = 1 # sizeof(char) FIXME
        elif dataType == "int":
            datatype_size = 4 # sizeof(int) FIXME
        elif dataType == "double":
            datatype_size = 8 # sizeof(double) FIXME

        boundary_limit_count = max_boundary // datatype_size
        Content = structGen.generate(boundary_limit_count, dataType)
        open(f"tmp/out_struct_boundaries_{dataType}.c", "w").write(Content)

        StdoutFile = Driver.run(
            [f"tmp/out_struct_boundaries_{dataType}.c", "src/helper.c"],
            ["src/arch/riscv.s"], f"out_struct_boundaries_{dataType}"
        )

        # As multiple calls are made to the "callee()" external function,
        #   we need to split the information in multiple dumps and for over
        #   each one of them.
        dump_sections = dumpInformation.split_dump_sections(StdoutFile)
        boundary_limit_count = 0
        for dump in dump_sections:
            boundary_limit_count += 1
            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(dump)

            # Retrive the stack address from the dump.
            stack_address = dump_information.get_header_info(0)

            reg_banks = dump_information.get_reg_banks()
            reg_bank = reg_banks[next(iter(dump_information.get_reg_banks()))]
            if structTests.if_stack_address_found(stack_address, reg_bank, Target):
                break

        # Removing 1 value as the limit count its being it actually used the stack.
        boundary_limit_count -= 1
        if ((boundary_limit_count) * datatype_size) != max_boundary:
            print(f"    {dataType} not expected boundary limits: {boundary_limit_count}")
        else:
            print(f"    {dataType} expected boundary limits: {boundary_limit_count}")

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

def do_tests(Driver, Report, Target):
     do_datatypes(Driver, Report)
     do_empty_struct(Driver, Report, Target)
     do_struct_boundaries(Driver, Report, Target)
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

    # Select Target.
    # Hardcoded to RISCV FIXME
    Target = targetArch.RISCV()

    # Set environment variable
    helper.set_env(cc_option, sim_option)

    # Initialize the report driver with the report name
    Report = reportDriver.ReportDriver(ReportName, OptionParser)

    print(f"Running {cc_option} with {sim_option}...")

    is_verbose = OptionParser.get('verbose')
    Driver = compilationDriver.CompilationDriver(is_verbose)

    # Run tests and generate summary report
    do_tests(Driver, Report, Target)
    Report.generateReport()
