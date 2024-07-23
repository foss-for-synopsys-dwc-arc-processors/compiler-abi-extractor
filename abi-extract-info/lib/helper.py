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

import re
# Responsible for parsing the standard output from the datatype
#  signedness/size/align test case for use in other test cases.
# This information will be stored in 'type_details' in the 'TargetArch' class.
def parse_type_info(text):
    lines = text.strip().split('\n')
    type_details = dict()

    for line in lines:
        type_name = re.search(r'^([\w\s\*]+)\s*', line)
        type_name = type_name.group(1) if type_name else None
        type_name = type_name.strip()

        signedness = re.search(r'signedness: (\d+)', line).group(1)
        size = re.search(r'size: (\d+)', line).group(1)
        align = re.search(r'align: (\d+)', line).group(1)

        type_details[type_name] = {
            "signedness": int(signedness),
            "size": int(size),
            "align": int(align)
        }

    return type_details
