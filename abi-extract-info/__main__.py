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

from analyzers.datatypes import DataTypesAnalyzer
from analyzers.saved import SavedAnalyzer
from analyzers.returnpass import ReturnAnalyzer
from analyzers.bitfield import BitFieldAnalyzer
from analyzers.argpass import ArgPassAnalyzer
from analyzers.struct_boundaries import StructBoundaryAnalyzer
from analyzers.endianness import EndiannessAnalyzer
from analyzers.stack_dir import StackDirAnalyzer
from analyzers.stack_align import StackAlignAnalyzer


ANALYZERS = [
    DataTypesAnalyzer,
    StackDirAnalyzer,
    StackAlignAnalyzer,
    ArgPassAnalyzer,
    StructBoundaryAnalyzer,
    EndiannessAnalyzer,
    SavedAnalyzer,
    ReturnAnalyzer,
    BitFieldAnalyzer,
    # ,, more different kind of tests here
]


def run_analyzers(Driver, Report, Target):
    for analyzer in ANALYZERS:
        analyzer(Driver, Report, Target).run()


if __name__ == "__main__":
    # Parse options
    OptionParser = optionParser.OptionParser().instance()
    OptionParser.option_parser()

    # Construct the report name from options
    cc_option = OptionParser.get("cc")
    sim_option = OptionParser.get("sim")
    ReportName = f"{cc_option}_{sim_option}.report"

    # Select Target.
    # Hardcoded to RISCV FIXME
    Target = targetArch.RISCV()

    # Set environment variable
    helper.set_env(cc_option, sim_option)

    # Initialize the report driver with the report name
    Report = reportDriver.ReportDriver(ReportName, OptionParser)

    print(f"Running {cc_option} with {sim_option}...")

    is_verbose = OptionParser.get("verbose")
    Driver = compilationDriver.CompilationDriver(is_verbose)

    # Run tests and generate summary report
    run_analyzers(Driver, Report, Target)
    Report.generateReport()

    if not OptionParser.get("save_temps"):
        helper.cleanup()
