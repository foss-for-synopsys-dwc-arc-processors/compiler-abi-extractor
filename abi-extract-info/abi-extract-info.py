#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import compilationDriver
import datatypesTests

def do_datatypes(Driver):
    Content = datatypesTests.generate()
    open("out_datatypes.c", "w").write(Content)
    Driver.compile("out_datatypes.c", "out_datatypes.s")
    Driver.assemble("out_datatypes.s", "out_datatypes.o")
    Driver.link("out_datatypes.o", "out_datatypes.elf")
    Driver.simulate("", "out_datatypes.elf", "out_datatypes.txt")

def do_tests(Driver):
     do_datatypes(Driver)
     # ,, more different kind of tests here

if __name__ == "__main__":
    Driver = compilationDriver.CompilationDriver()
    do_tests(Driver)
