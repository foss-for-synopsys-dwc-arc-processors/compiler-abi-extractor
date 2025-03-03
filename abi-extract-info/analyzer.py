# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import tempfile
import os


class AnalyzerError(Exception):
    """
    This exception is raised when something related to compilation has failed.
    """


class Analyzer:
    """
    This is the base class for every analyzer and handles the common operations
    performed by all analyzers.

    An analyzer performs the following steps:
        1) Generate or provide C source.
        2) Compile the source using the configured compiler.
        3) Run the compiled binary and capture its stdout.
        4) (Optionally) analyze stdout and use it to generate a report.
        5) Append the analysis results to the report.

    Steps 2, 3, and 5 are handled by this class. The others should be handled
    by the class overriding this one.

    An analyzer implementation is expected to call `Analyzer.__init__` with a
    name. This name will be used for debug logging and temporary file names.

    A basic implementation looks like this:
    ```
    class FooAnalyzer(Analyzer):
        def __init__(self, Driver, Report, Target, name):
            super().__init__(Driver, Report, Target, "foo")
            self.source_files += ["src/foo.c"]

        def analyze(self):
            return analyze_foo_stdout(self.generate(generate_foo_source()))
    ```
    """

    def __init__(self, Driver, Report, Target, name):
        self.Driver = Driver
        self.Report = Report
        self.Target = Target
        self.name = name
        self.source_files = ["src/helper.c"]
        self.assembly_files = ["src/arch/riscv.S"]

    def generate(self, srcs=None):
        """
        This method takes a (list of) string(s) containing C source code. It
        will compile it for you and run it and provide the caller with a
        string containing the stdout of the compiled C program.

        Providing an argument is optional. If none is specified, just the
        members of `self.source_files` and `self.assembly_files` will be
        compiled.
        """
        if srcs is None:
            srcs = []
        if not isinstance(srcs, list):
            srcs = [srcs]
        temp_source_files = []
        for src in srcs:
            (handle, temp_source_file) = tempfile.mkstemp(
                suffix=".c", prefix=self.name, dir="tmp/", text=True
            )
            with os.fdopen(handle, "w") as file:
                file.write(src)
            temp_source_files.append(temp_source_file)
        res, stdout_file = self.Driver.run(
            self.source_files + temp_source_files,
            self.assembly_files,
            self.name,
        )
        if res != 0:
            raise AnalyzerError
        with open(stdout_file, "r", encoding="utf-8") as file:
            return file.read()

    def analyze(self):
        """
        A subclass will usually override this method.
        It is expected to compile the C program and interpret its stdout. The
        string that is returned by this method will be appended to the report.

        Overriding this method is optional if one provides the C source by
        appending self.source_files and the stdout of the program can be
        appended to the report as is.
        """
        return self.generate()

    def run(self):
        """
        Runs the analyzer and attaches the analysis result to the report.
        """
        try:
            summary_content = self.analyze()
            summary_file = f"tmp/{self.name}.sum"
            with open(summary_file, "w", encoding="utf-8") as file:
                file.write(summary_content)
            self.Report.append(summary_file)
        except AnalyzerError:
            print(f"Skip: '{self.name}' analyzer failed.")
