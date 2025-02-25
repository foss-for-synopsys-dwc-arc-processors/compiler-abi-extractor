# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

.data
.text
.globl foo
foo:
    addi sp, sp, -8
    sw ra, 0(sp)

    call bar
    call callee

    lw ra, 0(sp)
    addi sp, sp, 8

    ret
