#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import subprocess

class CompilationDriver:
    def __init__(self):
        self.cc = "gcc"
        self.assembler = "gcc"
        self.linker = "gcc"
        self.simulator = "wrapper_x86"
        self.cflags = ["-O1"]

    def isWindows(self):
        return False # For now, later on, we can also support windows

    def info(self, W):
        print("%s" % W)

    # c: an array of arguments. The first element is the program to execute.
    def cmd(self, c, stdout=None, stderr=None, env=None):
        if self.isWindows() and c[0]=="bash":
            c=[c[0], "-o", "igncr"]+c[1:]
        self.info("EXECUTING: %s" % (" ".join(c)))
        return subprocess.call(c, stdout=stdout, stderr=stderr, env=env)

    # c: an array of arguments. The first element is the program to execute.
    # Returns the output
    def cmdWithResult(self, c, errorMsg=None, env=None):
        try:
            self.info("EXECUTING: %s" % (" ".join(c)))
            return subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        except OSError as oserror:
            return None

    # Compiler the specified program into an object file
    def compile(self, InputFile, OutputFile):
        self.cmd([self.cc] + self.cflags + [InputFile, "-S", "-o", OutputFile])

    def assemble(self, InputFile, OutputFile):
        self.cmd([self.assembler] + self.cflags + [InputFile, "-c", "-o", OutputFile])

    def link(self, InputFile, OutputFile):
        self.cmd([self.linker] + self.cflags + [InputFile, "-o", OutputFile])

    def simulate(self, args, InputFile, OutputFile):
        Content = self.cmdWithResult([self.simulator] + [InputFile]).decode()
        open(OutputFile, "w").write(Content)
