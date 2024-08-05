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

def do_datatypes(Driver, Report, Target):
    Content = datatypesTests.generate()
    open("tmp/out_datatypes.c", "w").write(Content)
    stdoutFile = Driver.run(["tmp/out_datatypes.c"], [], "out_datatypes")

    # Reading the file generated by the C program executed.
    Stdout = helper.read_file(stdoutFile)
    # Parsing the type details (signedness/size/align) into the 'targetArch' class.
    Target.set_type_details(helper.parse_type_info(Stdout))

    # Store the generated report file for datatypes test case.
    #Report.append(stdoutFile)

def do_argpass(Driver, Report, Target):
    # List of datatypes to be tested.
    types = [ "char", "short", "int", "long", "long long",
              "float", "double", "long double"]

    results = {}
    for T in types:
        # Skip `long double` due to its size limitations. FIXME
        if T == "long double":
            continue

        # Create an instance of `ArgPassTests` for the current Target
        arg_pass_tests = argPassTests.ArgPassTests(Target)


        for count in range(1, 17):
            # Generate hexadecimal values for the current datatype and count
            value_list = helper.generate_hexa_values(Target, T, count)
            # Generate the content of the test file.
            Content = argPassTestsGen.generate(Target, T, value_list)

            # Create and write the test file.
            T_file = T.replace(' ','_')
            open(f"tmp/{T_file}.c", "w").write(Content)
            # Compile and run the test file, and capture the stdout.
            StdoutFile = Driver.run([f"tmp/{T_file}.c", "src/helper.c"], ["src/arch/riscv.s"], f"{T_file}")

            # Parse the stdout to extract stack and register bank information.
            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(StdoutFile, True)

            # Get the stack and register bank information
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()
            # Run the test to check if the value is in the stack
            is_value_in_stack = arg_pass_tests.run_test(stack, reg_banks, value_list)

            # If the value is found in the stack, stop further test iterations
            # for this datatype.
            if is_value_in_stack == True:
                break

        # Get the last iteration results
        last_iteration = arg_pass_tests.results[-1]
        argc = last_iteration["argc"] - 1
        argr = last_iteration["registers"]
        are_values_on_stack = last_iteration["value_in_stack"]
        are_values_splitted = last_iteration["value_split_order"]

        # Initialize the results dictionary for the current argument count,
        # if not already present.
        if argc not in results:
            results[argc] = { "type": [], "regs": [],
                              "common_regs": [], "noncommon_regs": [],
                              "are_values_on_stack": False,
                              "are_values_splitted": [] }

        # Append the current datatype and register information to the results
        results[argc]["type"].append(T)
        results[argc]["regs"].append(argr)
        results[argc]["are_values_on_stack"] = are_values_on_stack
        results[argc]["are_values_splitted"] = are_values_splitted

    # Process the results to extract common and non-common registers used.
    for rkey, rvalue in results.items():
        common_regs, noncommon_regs = arg_pass_tests.extract_common_regs(rvalue["regs"])
        rvalue["common_regs"] = common_regs
        rvalue["noncommon_regs"] = noncommon_regs

    # Write a summary report from the results.
    Content = arg_pass_tests.create_summary_string(results)
    open("tmp/out_argPassTests.sum", "w").write(Content)
    Report.append("tmp/out_argPassTests.sum")

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
    types = [ "char", "signed char", "unsigned char", "short", "int", "long",
              "long long", "void*", "float", "double", "long double"]

    # For RISCV 32-bit, if a struct exceeds 16 bytes in size for argument
    #  passing, the reference address in `a0` will not correspond to the
    #  stack pointer but will include an offset, causing issues with the
    #  current logic.
    # TODO: Test for 64-bit scenarios.

    int_size = Target.get_type_details("int")["size"]

    # Initially, the `max_boundary` was set to twice the size of an `int`,
    #  based on the RISCV ABI document. However, this approach is adjusted
    #  to use the size of a `char` to define the limits, as the previous
    #  assumption may not apply to other architectures. The size of an `int`
    #  is still used to finalize the `max_boundary` value.

    # Note: The `-1` adjustment accounts for the fact that `structGen` adds
    #  a `char` after the `max_boundary` limit. Given the issue described above,
    #  the total size for 32-bit should not exceed 16 bytes.
    max_boundary = 2 * int_size * 2 - 1
    boundary_limit_count = 0

    for dataType in types:
        # Get datatype size from stored information from previous test case.
        datatype_size = Target.get_type_details(dataType)["size"]

        boundary_limit_count = max_boundary // datatype_size
        values_list = helper.generate_hexa_values(Target, dataType, boundary_limit_count + 1)
        Content = structGen.generate(boundary_limit_count, dataType, values_list)
        open(f"tmp/out_struct_boundaries_{dataType}.c", "w").write(Content)

        StdoutFile = Driver.run(
            [f"tmp/out_struct_boundaries_{dataType}.c", "src/helper.c"],
            ["src/arch/riscv.s"], f"out_struct_boundaries_{dataType}"
        )

        struct_tests = structTests.StructTests(Target)

        # As multiple calls are made to the "callee()" external function,
        #   we need to split the information in multiple dumps and for over
        #   each one of them.
        dump_sections = dumpInformation.split_dump_sections(StdoutFile)
        boundary_limit_count = 0
        for index, dump in enumerate(dump_sections):
            count = index + 1
            # Generate hexadecimal values for the current datatype and count
            value_list = helper.generate_hexa_values(Target, dataType, count)
            boundary_limit_count += 1
            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(dump)

            # Get stack and register bank information
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()

            # Retrive the stack address from the dump.
            stack_address = dump_information.get_header_info(0)

            is_passed_by_ref = struct_tests.run_test(stack_address, stack, reg_banks, value_list)
            if is_passed_by_ref == True:
                break

        # Get the last iteration results
        last_iteration = struct_tests.results[-1]
        argc = last_iteration["argc"] - 1
        argr = last_iteration["registers"]
        are_values_on_stack = last_iteration["value_in_stack"]
        are_values_splitted = last_iteration["value_split_order"]

        # Initialize the results dictionary for the current argument count,
        # if not already present.
        if argc not in results:
            results[argc] = { "type": [], "regs": [],
                              "common_regs": [], "noncommon_regs": [],
                              "are_values_on_stack": False,
                              "are_values_splitted": [] }

        # Append the current datatype and register information to the results
        results[argc]["type"].append(dataType)
        results[argc]["regs"].append(argr)
        results[argc]["are_values_on_stack"] = are_values_on_stack
        results[argc]["are_values_splitted"] = are_values_splitted

    # Process the results to extract common and non-common registers used.
    for rkey, rvalue in results.items():
        common_regs, noncommon_regs = struct_tests.extract_common_regs(rvalue["regs"])
        rvalue["common_regs"] = common_regs
        rvalue["noncommon_regs"] = noncommon_regs

    # Write a summary report from the results.
    Content = struct_tests.create_summary_string(results)
    open("tmp/out_struct_boundaries.sum", "w").write(Content)
    Report.append("tmp/out_struct_boundaries.sum")


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
     do_datatypes(Driver, Report, Target)
     do_argpass(Driver, Report, Target)
    #  do_empty_struct(Driver, Report, Target)
    #  do_struct_boundaries(Driver, Report, Target)
    #  do_argpass(Driver, Report)
    #  do_endianness(Driver, Report)
    #  do_stack_dir(Driver, Report)
    #  do_stack_align(Driver, Report)
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
