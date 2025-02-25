# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

def do_stack_dir(Driver, Report):
    source_files   = ["src/stack_dir/main.c", \
                      "src/stack_dir/A.c", "src/stack_dir/B.c"]
    assembly_files = []
    output_name = "out_stackdir"
    res, stdoutFile = Driver.run(source_files, assembly_files, output_name)
    if res != 0:
        print("Skip: Stack Direction test case failed.")
        return
    Report.append(stdoutFile)
