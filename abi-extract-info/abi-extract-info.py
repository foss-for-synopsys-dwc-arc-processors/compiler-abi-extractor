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
    open("out_datatypes.c", "w").write(Content)
    Driver.compile("out_datatypes.c", "out_datatypes.s")
    Driver.assemble("out_datatypes.s", "out_datatypes.o")
    Driver.link("out_datatypes.o", "out_datatypes.elf")
    Driver.simulate("", "out_datatypes.elf", "out_datatypes.txt")

def do_argpass(Driver):
    Driver.compile("src/argpass/caller.c", "out_caller.s")
    Driver.assemble("out_caller.s", "out_caller.o")
    Driver.assemble("src/argpass/riscv/callee.s", "out_callee.o")
    Driver.link(["out_callee.o", "out_caller.o"], "out_argpass.elf")
    Driver.simulate("", "out_argpass.elf", "out_argpass.stdout")
    Content = argPassTests.parser("out_argpass.stdout")
    open("out_argpass.txt", "w").write(" ".join(Content))

def do_tests(Driver):
     do_datatypes(Driver)
     do_argpass(Driver)
     # ,, more different kind of tests here

if __name__ == "__main__":
    Driver = compilationDriver.CompilationDriver()
    do_tests(Driver)
