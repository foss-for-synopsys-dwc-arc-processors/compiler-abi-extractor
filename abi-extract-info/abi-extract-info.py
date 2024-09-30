#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib import compilationDriver
from lib import reportDriver
from lib import datatypesGen
from lib import datatypesTests
from lib import stackAlignTests
from lib import argPassTests
from lib import argPassTestsGen
from lib import optionParser
from lib import helper

from lib import emptyStructGen
from lib import emptyStructTests
from lib import dumpInformation
from lib import targetArch
from lib import structGen
from lib import structTests
from lib import returnGen
from lib import returnTests
from lib import savedGen
from lib import savedTests
from lib import bitFieldGen
from lib import bitFieldTests

import sys

def do_datatypes(Driver, Report, Target):
    Content = datatypesGen.generate()
    open("tmp/out_datatypes.c", "w").write(Content)
    stdoutFile = Driver.run(["tmp/out_datatypes.c"], [], "out_datatypes")

    # Reading the file generated by the C program executed.
    Stdout = helper.read_file(stdoutFile)
    # Parsing the type details (signedness/size/align) into the 'targetArch' class.
    Target.set_type_details(helper.parse_type_info(Stdout))

    content = datatypesTests.generate(Stdout)
    open("tmp/out_datatypes.sum", "w").write(content)

    # Store the generated report file for datatypes test case.
    Report.append("tmp/out_datatypes.sum")

def do_saved(Driver, Report, Target):
    sizeof = Target.get_type_details("int")["size"]
    content = savedGen.generate_main(Target, sizeof)
    open("tmp/out_saved_main.c", "w").write(content)
    content = savedGen.generate_aux(Target, sizeof)
    open("tmp/out_saved_aux.c", "w").write(content)
    stdout_file = Driver.run(
        ["tmp/out_saved_main.c", "tmp/out_saved_aux.c", "src/helper.c"],
        ["src/arch/riscv.S"], "out_saved"
    )

    dump_information = dumpInformation.DumpInformation()
    dump_information.parse(stdout_file, True)
    register_banks = dump_information.get_reg_banks()

    saved_tests = savedTests.SavedTests(Target)
    summary_content = saved_tests.run_test(register_banks, sizeof)

    summary_file = "tmp/out_saved.sum"
    open(summary_file, "w").write(summary_content)

    # Store the generated report file for argument passing test case.
    Report.append(summary_file)

def do_return(Driver, Report, Target):
    dtypes = ["char", "short", "int", "long",
             "long long", "float", "double", "long double"]

    # TODO You need to handle `long double` differently if its
    # 16 bytes in a 32 bit machine.

    return_tests = returnTests.ReturnTests(Target)
    results = {}
    for dtype in dtypes:
        results[dtype] = []

        sizeof = Target.get_type_details(dtype)["size"]
        content = returnGen.generate_single_call(Target, None, dtype, sizeof)
        open(f"tmp/out_return_{dtype}.c", "w").write(content)

        stdout_file = Driver.run(
            [f"tmp/out_return_{dtype}.c", "src/helper.c"],
            ["src/arch/riscv.S", "src/arch/riscv2.s"], f"out_return_{dtype}"
        )

        argv = helper.generate_hexa_values_2(sizeof, 20)

        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout_file, True)

        # Get stack and register bank information
        stack = dump_information.get_stack()
        register_banks = dump_information.get_reg_banks()

        citeration = {}
        return_tests.run_test(citeration, stack, register_banks, argv)
        results[dtype].append(citeration)

    summary_content = return_tests.generate_summary(results)
    summary_file = "tmp/out_return.sum"
    open(summary_file, "w").write(summary_content)

    # Store the generated report file for return test case.
    Report.append(summary_file)

def do_bitfield(Driver, Report, Target):
    content = bitFieldGen.generate()
    open("tmp/out_bitfield.c", "w").write(content)
    stdout_file = Driver.run(["tmp/out_bitfield.c"], [], "out_bitfield")
    content = helper.read_file(stdout_file)

    summary_content = bitFieldTests.prepare_summary(content)
    summary_file = "tmp/out_bitfield.sum"
    open(summary_file, "w").write(summary_content)
    Report.append(summary_file)

def do_argpass(Driver, Report, Target):
    # List of datatypes to be tested.
    types = [ "char", "short", "int", "long", "long long",
              "float", "double", "long double"]

    results = {}
    for dtype in types:
        # Skip `long double` due to its size limitations. FIXME
        if dtype == "long double":
            continue

        # Create an instance of `ArgPassTests` for the current Target
        arg_pass_tests = argPassTests.ArgPassTests(Target)

        dtype_sizeof = Target.get_type_details(dtype)["size"]

        argc = 1
        while (True):
            # Generate hexadecimal values for the current datatype and count
            argv = helper.generate_hexa_list(argc, dtype_sizeof, 10)

            # Generate the content of the test file.
            content = argPassTestsGen.generate(Target, dtype, argv)

            # Create and write the test file.
            dtype_file = dtype.replace(' ','_')
            open(f"tmp/out_argpass_{dtype_file}_{argc}.c", "w").write(content)
            # Compile and run the test file, and capture the stdout.
            StdoutFile = Driver.run([f"tmp/out_argpass_{dtype_file}_{argc}.c", "src/helper.c"], ["src/arch/riscv.S"], f"out_argpass_{dtype_file}_{argc}")

            # Parse the stdout to extract stack and register bank information.
            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(StdoutFile, True)

            # Get the stack and register bank information
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()
            # Run the test to check if the value is in the stack
            citeration = arg_pass_tests.run_test(stack, reg_banks, argv)

            if citeration["value_in_stack"]:
                break

            if argc == 20:
                print("DEBUG: Exitting for save purposes. [do_argpas]")
                break

            argc += 1

        # Get the last iteration results
        last_iteration = citeration
        argc = last_iteration["argc"] - 1
        argr = last_iteration["registers"]
        are_values_on_stack = last_iteration["value_in_stack"]
        are_values_splitted = last_iteration["pairs_order"]
        inconsistencies = last_iteration["inconsistencies"]

        Target.set_argument_registers_2(dtype, citeration["registers"])

        # Initialize the results dictionary for the current argument count,
        # if not already present.
        if argc not in results:
            results[argc] = { "type": [], "regs": [],
                              "common_regs": [], "noncommon_regs": [],
                              "are_values_on_stack": False,
                              "are_values_splitted": [],
                              "inconsistencies": [] }

        # Append the current datatype and register information to the results
        results[argc]["type"].append(dtype)
        results[argc]["regs"].append(argr)
        results[argc]["are_values_on_stack"] = are_values_on_stack
        results[argc]["are_values_splitted"] = are_values_splitted
        results[argc]["inconsistencies"] = inconsistencies

    # Process the results to extract common and non-common registers used.
    for rkey, rvalue in results.items():
        common_regs, noncommon_regs = arg_pass_tests.extract_common_regs(rvalue["regs"])
        rvalue["common_regs"] = common_regs
        rvalue["noncommon_regs"] = noncommon_regs

    # Write a summary report from the results.
    Content = arg_pass_tests.create_summary_string(results)
    open("tmp/out_argPassTests.sum", "w").write(Content)
    Report.append("tmp/out_argPassTests.sum")

def do_empty_struct(Driver, Report, Target):
    # This value is to be defined according to number for
    # argument passing in registers from "do_argpass" test case.
    MaxCallCount = 8 # Current static value. FIXME
    Content = emptyStructGen.generate(MaxCallCount)
    open("tmp/out_emptyStruct.c", "w").write(Content)

    StdoutFile = Driver.run(["tmp/out_emptyStruct.c", "src/helper.c"], ["src/arch/riscv.S"], "out_emptyStruct")
    content = emptyStructTests.split_sections(StdoutFile, Target)
    return content

def do_struct_boundaries(Driver, Report, Target):
    # TODO: Test for 64-bit scenarios.

    int_size = Target.get_type_details("int")["size"]

    # The max_boundary is calculated with the `char` datatype.
    # The test case will generate multiple C files to test the struct
    # boundaries, char by char. Once it reaches the stack as reference,
    # the max_boundary is defined.
    max_boundary = 0

    # CHAR
    dtype = "char"
    results = {}
    results[dtype] = []
    sizeof = Target.get_type_details(dtype)["size"]

    count = 0
    while (True):
        Content = structGen.generate_single_call(Target, count, dtype, sizeof)
        open(f"tmp/out_struct_boundaries_{dtype}_{count}.c", "w").write(Content)

        stdout_file = Driver.run(
            [f"tmp/out_struct_boundaries_{dtype}_{count}.c", "src/helper.c"],
            ["src/arch/riscv.S"], f"out_struct_boundaries_{dtype}_{count}"
        )

        struct_tests = structTests.StructTests(Target)

        res = count + 1 # +1 to generate extra char at the end.
        argv = helper.generate_hexa_list(res, sizeof, count)

        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout_file, True)

        # Get stack and register bank information
        stack = dump_information.get_stack()
        reg_banks = dump_information.get_reg_banks()

        # Retrive the stack addresses from the dump.
        #stack_address = dump_information.get_header_info(0)
        stack_address = None

        citeration = {}
        struct_tests.run_test(citeration, dtype, stack, reg_banks, argv)
        results[dtype].append(citeration)
        if citeration["passed_by_ref"] != None:
            break

        count += 1

        if count == 10:
            print("breaking for safe purposes [struct_boundaries]")
            break


    max_boundary = count

    struct_tests = structTests.StructTests(Target)
    # `long double` needs a different treating because its size
    # can be 16 bytes in a 32-bit architecture. That means that
    # the values are splitten in 4, and so that implementation
    # is yet to be added. FIXME
    types = ["short", "int", "long",
             "long long", "float", "double"]
    for dtype in types:
        results[dtype] = []

        # Get datatype size from stored information from previous test case.
        sizeof = Target.get_type_details(dtype)["size"]

        # Calculate max datatype boundary according to sizeof
        boundary_limit_count = max_boundary // sizeof
        Content = structGen.generate_multiple_call(Target, boundary_limit_count, dtype, sizeof)
        open(f"tmp/out_struct_boundaries_{dtype}.c", "w").write(Content)

        StdoutFile = Driver.run(
            [f"tmp/out_struct_boundaries_{dtype}.c", "src/helper.c"],
            ["src/arch/riscv.S"], f"out_struct_boundaries_{dtype}"
        )

        # As multiple calls are made to the "callee()" external function,
        # we need to split the information in multiple dumps and for over
        # each one of them.
        dump_sections = dumpInformation.split_dump_sections(StdoutFile)
        for index, dump in enumerate(dump_sections):

            count = index + 1 # +1 to generate extra char at the end.
            argv = helper.generate_hexa_list(count, sizeof, 10 if count == 1 else None)

            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(dump)

            # Get stack and register bank information
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()

            # Retrive the stack addresses from the dump.
            #stack_address = dump_information.get_header_info(0)
            stack_address = None

            citeration = {}
            struct_tests.run_test(citeration, dtype, stack, reg_banks, argv)
            results[dtype].append(citeration)
            if citeration["passed_by_ref"] != None:
                break

        _boundary = len(results[dtype])
        _boundary += -1 if _boundary > 0 else 0

    content = struct_tests.prepare_summary(results)
    content += do_empty_struct(Driver, Report, Target)
    open("tmp/out_structs.sum", "w").write(content)

    # Store the generated report file for struct argumnet passing test case.
    Report.append("tmp/out_structs.sum")

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

    # `src/heler.c` has been added as a placeholder for the dump_information function
    # as it is called within the `callee` function in `src/arch/riscv.s`.
    # Although this function is not used, it is present in the riscv.s file.
    stdoutFile = Driver.run(["tmp/out_functions.c", "tmp/out_driver.c", "src/helper.c"], ["src/arch/riscv.S"], "out_stackalign")
    Report.append(stdoutFile)

def do_tests(Driver, Report, Target):
    do_datatypes(Driver, Report, Target)
    do_stack_dir(Driver, Report)
    do_stack_align(Driver, Report)
    do_argpass(Driver, Report, Target)
    do_struct_boundaries(Driver, Report, Target)
    do_endianness(Driver, Report)
    do_saved(Driver, Report, Target)
    do_return(Driver, Report, Target)
    do_bitfield(Driver, Report, Target)
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

    if not OptionParser.get("save_temps"):
        helper.cleanup()
