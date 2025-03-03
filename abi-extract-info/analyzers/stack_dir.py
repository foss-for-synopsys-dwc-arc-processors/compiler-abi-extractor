# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import analyzer
import helper


class StackDirAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "stack_dir")
        self.source_files += [
            "src/stack_dir/main.c",
            "src/stack_dir/A.c",
            "src/stack_dir/B.c",
        ]
