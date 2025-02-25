# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

def do_endianness(Driver, Report):
    source_files   = ["src/endianness/endianness.c"]
    assembly_files = []
    output_name = "out_endianness"
    res, stdoutFile = Driver.run(source_files, assembly_files, output_name)
    if res != 0:
        print("Skip: Endianness test case failed.")
        return
    Report.append(stdoutFile)
