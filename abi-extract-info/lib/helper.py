#! /bin/env python
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import os

# Add the compiler and simulator wrappers to the
# PATH environment variable to enable a modular
# approach for invoking various compilers and simulators.
def set_env(cc, sim):
    root_path = os.path.abspath(".")
    wrapper_path = root_path + "/scripts/wrapper/"

    # Set environment variable
    os.environ["PATH"] = wrapper_path + f"/cc/{cc}:" + os.environ["PATH"]
    os.environ["PATH"] = wrapper_path + f"/sim/{sim}:" + os.environ["PATH"]
