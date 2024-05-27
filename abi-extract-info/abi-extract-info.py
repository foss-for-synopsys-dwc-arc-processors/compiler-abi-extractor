#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import compilationDriver
import datatypesTests
import argPassTests

def do_datatypes(Driver):
    Content = datatypesTests.generate()
    open("tmp/out_datatypes.c", "w").write(Content)
    Driver.compile("tmp/out_datatypes.c", "tmp/out_datatypes.s")
    Driver.assemble("tmp/out_datatypes.s", "tmp/out_datatypes.o")
    Driver.link("tmp/out_datatypes.o", "tmp/out_datatypes.elf")
    Driver.simulate("", "tmp/out_datatypes.elf", "tmp/out_datatypes.txt")

def do_argpass(Driver):
    Driver.compile("src/argpass/caller.c", "tmp/out_caller.s")
    Driver.assemble("tmp/out_caller.s", "tmp/out_caller.o")
    Driver.assemble("src/argpass/riscv/callee.s", "tmp/out_callee.o")
    Driver.link(["tmp/out_callee.o", "tmp/out_caller.o"], "tmp/out_argpass.elf")
    Driver.simulate("", "tmp/out_argpass.elf", "tmp/out_argpass.stdout")
    Content = argPassTests.parser("tmp/out_argpass.stdout")
    open("tmp/out_argpass.txt", "w").write(" ".join(Content))

def do_tests(Driver):
     do_datatypes(Driver)
     do_argpass(Driver)
     # ,, more different kind of tests here

if __name__ == "__main__":
    Driver = compilationDriver.CompilationDriver()
    do_tests(Driver)
