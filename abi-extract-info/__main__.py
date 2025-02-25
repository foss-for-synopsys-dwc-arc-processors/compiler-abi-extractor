#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import compilationDriver
import reportDriver
import optionParser
import helper
import targetArch

from analyzers.datatypes         import do_datatypes
from analyzers.saved             import do_saved
from analyzers.returnpass        import do_return
from analyzers.bitfield          import do_bitfield
from analyzers.argpass           import do_argpass
from analyzers.struct_boundaries import do_struct_boundaries
from analyzers.endianness        import do_endianness
from analyzers.stack_dir         import do_stack_dir
from analyzers.stack_align       import do_stack_align

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
