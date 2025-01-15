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

    # Generate value for callee/caller saved registers.
    helper.reset_used_values()
    hvalue_caller_saved = helper.generate_hexa_value(sizeof)
    hvalue_callee_saved = helper.generate_hexa_value(sizeof)

    content = savedGen.generate_main(Target, hvalue_caller_saved)
    open("tmp/out_saved_main.c", "w").write(content)
    content = savedGen.generate_aux(Target, hvalue_callee_saved)
    open("tmp/out_saved_aux.c", "w").write(content)
    stdout_file = Driver.run(
        ["tmp/out_saved_main.c", "tmp/out_saved_aux.c", "src/helper.c"],
        ["src/arch/riscv.S"], "out_saved"
    )

    dump_information = dumpInformation.DumpInformation()
    dump_information.parse(stdout_file, True)
    register_banks = dump_information.get_reg_banks()

    saved_tests = savedTests.SavedTests(Target)
    summary_content = saved_tests.run_test(register_banks, \
                                hvalue_caller_saved, hvalue_callee_saved)

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

        # Get the sizeof the current data type.
        sizeof = Target.get_type_details(dtype)["size"]
        # Reset the already used values.
        helper.reset_used_values()
        # Generate a single hexadecimal value.
        hvalue_return = helper.generate_hexa_value(sizeof)

        # Generate and build/execute the test case.
        content = returnGen.generate_single_call(Target, dtype, hvalue_return)
        dtype_ = dtype.replace(' ', '_')
        open(f"tmp/out_return_{dtype_}.c", "w").write(content)

        stdout_file = Driver.run(
            [f"tmp/out_return_{dtype_}.c", "src/helper.c"],
            ["src/arch/riscv.S", "src/arch/riscv2.s"], f"out_return_{dtype_}"
        )

        # Parse the dump information.
        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout_file, True)

        # Get stack and register bank information
        stack = dump_information.get_stack()
        register_banks = dump_information.get_reg_banks()

        citeration = {}
        return_tests.run_test(citeration, stack, register_banks, hvalue_return)
        results[dtype].append(citeration)

    summary_content = return_tests.generate_summary(results)
    summary_file = "tmp/out_return.sum"
    open(summary_file, "w").write(summary_content)

    # Store the generated report file for return test case.
    Report.append(summary_file)

def do_bitfield(Driver, Report, Target):
    content = bitFieldGen.generate(Target)
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
        results[dtype] = []

        argc = 1
        while (True):
            # Generate hexadecimal values for the current datatype and count
            helper.reset_used_values()
            argv = helper.generate_hexa_list(argc, dtype_sizeof)

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

            results[dtype].append(citeration)
            if citeration["value_in_stack"]:
                break

            if argc == 20:
                print("DEBUG: Exitting for save purposes. [do_argpas]")
                break

            argc += 1

        Target.set_argument_registers_2(dtype, citeration["registers"])

    # Process the results
    Content = arg_pass_tests.process_stages(results)

    # Write a summary report from the results.
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

    # The `char_limit` is calculated with the `char` datatype.
    # The test case will generate multiple C files to test the struct
    # boundaries, char by char. Once it reaches the stack as reference,
    # the `char_limit` is defined.
    # Start the char limit count with 1.
    char_limit = 1
    dtype = "char"
    results = {}
    results[dtype] = []
    char_sizeof = Target.get_type_details(dtype)["size"]

    # Reset the used generated values.
    helper.reset_used_values()
    while (True):
        # Generate a hexadecimal value list according to the current count.
        hvalues = helper.generate_hexa_list(char_limit, char_sizeof)

        # Generate and build/execute the test case.
        dtypes = [dtype] * char_limit
        Content = structGen.generate_single_call(Target, char_limit, dtypes, \
                                                 hvalues)
        file_name = f"out_struct_boundaries_{dtype}_{char_limit}"
        c_file_name = f"tmp/{file_name}.c"
        open(c_file_name, "w").write(Content)
        stdout_file = Driver.run(
            [c_file_name, "src/helper.c"],
            ["src/arch/riscv.S"], file_name
        )

        struct_tests = structTests.StructTests(Target)

        # Parse the dump information.
        dump_information = dumpInformation.DumpInformation()
        dump_information.parse(stdout_file, True)

        # Get stack and register bank information.
        stack = dump_information.get_stack()
        reg_banks = dump_information.get_reg_banks()

        citeration = {}
        struct_tests.run_test(citeration, dtype, stack, reg_banks, hvalues)
        results[dtype].append(citeration)
        if citeration["passed_by_ref"] != None:
            break

        # The struct has not been passed by reference yet, so increment
        # the char limit by one.
        char_limit += 1
        if char_limit == 10:
            print("breaking for safe purposes [struct_boundaries]")
            break

    # Reset used values.
    helper.reset_used_values()
    # Set back to the char's limit as its currently out of bounds.
    char_limit -= 1

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
        sizeof_dtype = Target.get_type_details(dtype)["size"]

        # FIXME! It has been observed that with floating-point registers
        # for double, the expected limit is different.
        # I.e, 16 instead of8 bytes.
        if dtype == "double":
            char_limit = char_limit * 2

        # Calculate max datatype boundary according to sizeof.
        limit_dtype = char_limit // sizeof_dtype

        # Generate the struct hexadecimal values with a list of data types.
        # Plus one char to validate the limit.
        for index, i in enumerate([[], ["char"]]):
            dtypes_ = [dtype] * limit_dtype + i
            hvalues_ = helper.generate_hexa_list_from_datatypes(dtypes_, Target)

            # Generate and build/execute the test case.
            Content = structGen.generate_single_call(Target, None, dtypes_, \
                                                     hvalues_)
            file_name = f"out_struct_boundaries_{dtype}_{index}"
            c_file_name = f"tmp/{file_name}.c"
            open(c_file_name, "w").write(Content)
            StdoutFile = Driver.run(
                [c_file_name, "src/helper.c"],
                ["src/arch/riscv.S"], file_name
            )

            # Parse the dump information.
            dump_information = dumpInformation.DumpInformation()
            to_read = True
            dump_information.parse(StdoutFile, to_read)

            # Get stack and register bank information
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()

            citeration = {}
            struct_tests.run_test(citeration, dtype, stack, reg_banks, hvalues)
            results[dtype].append(citeration)
            if citeration["passed_by_ref"] != None:
                break

        _boundary = len(results[dtype])
        _boundary += -1 if _boundary > 0 else 0

    content = struct_tests.prepare_summary(results)
    # Run the empty struct test case.
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
