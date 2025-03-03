# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import analyzer
import helper


class EndiannessAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "endianness")
        self.source_files += ["src/endianness/endianness.c"]
