# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import subprocess

def compilation(**params):

    cc          = params.get("cc", "cc")
    cflags      = params.get("cflags", "")
    input_file  = params.get("_input")
    output_file = params.get("output")

    cmd = f"{cc} {input_file} {cflags} -o {output_file}"
    
    print(cmd)

    result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


    assert (result.returncode == 0)
