#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
import subprocess

class CompilationDriver:
    def __init__(self, is_verbose):
        self.cc = "cc-wrapper"
        self.assembler = "as-wrapper"
        self.linker = "ld-wrapper"
        self.simulator = "sim-wrapper"
        self.cflags = ["-O1"]
        self.is_verbose = is_verbose

    def isWindows(self):
        return False # For now, later on, we can also support windows

    def info(self, W):
        print("%s" % W)

    # c: an array of arguments. The first element is the program to execute.
    def cmd(self, c, stdout=None, stderr=None, env=None):
        if self.isWindows() and c[0]=="bash":
            c=[c[0], "-o", "igncr"]+c[1:]
        # If the verbose flag (-v) is detected, executed commands will be
        # displayed along with their stdout and stderr outputs.
        if self.is_verbose:
            self.info("EXECUTING: %s" % (" ".join(c)))
            return subprocess.call(c, stdout=stdout, stderr=stderr, env=env)
        else:
            return subprocess.call(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

    # c: an array of arguments. The first element is the program to execute.
    # Returns the output
    def cmdWithResult(self, c, errorMsg=None, env=None):
        try:
            # If the verbose flag (-v) is detected, executed commands will be displayed.
            if self.is_verbose:
                self.info("EXECUTING: %s" % (" ".join(c)))
            return subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        except OSError as oserror:
            return None

    # Compile, assemble, link and simulate wrapper to reduce extensive code.
    def run(self, srcFiles, asmFiles, outFile, tmp="tmp/"):
        for srcFile in srcFiles:
            asmFile = tmp + os.path.basename(srcFile)
            asmFile = asmFile.replace(".c", ".s")
            self.compile(srcFile, asmFile)
            asmFiles.append(asmFile)

        objFiles = []
        for asmFile in asmFiles:
            objFile = tmp + os.path.basename(asmFile)
            objFile = objFile.replace(".s", ".o")
            self.assemble(asmFile, objFile)
            objFiles.append(objFile)

        outputFile = tmp + outFile + ".elf"
        self.link(objFiles, outputFile)

        stdoutFile = tmp + outFile + ".stdout"
        self.simulate("", outputFile, stdoutFile)

        return stdoutFile

    # Compiler the specified program into an object file
    def compile(self, InputFile, OutputFile):
        self.cmd([self.cc] + self.cflags + [InputFile, "-S", "-o", OutputFile])

    def assemble(self, InputFile, OutputFile):
        self.cmd([self.assembler] + self.cflags + [InputFile, "-c", "-o", OutputFile])

    # Initialy, only one input file was needed, but now multiple files are required
    # for expanded tests. A mechanism was added to handle multiple files, converting
    # a single file into a list of necessary.
    def link(self, InputFile, OutputFile):
        if isinstance(InputFile, str):
            InputFile = [InputFile]
        self.cmd([self.linker] + self.cflags + InputFile + ["-o", OutputFile])

    def simulate(self, args, InputFile, OutputFile):
        Content = self.cmdWithResult([self.simulator] + [InputFile]).decode()
        open(OutputFile, "w").write(Content)
