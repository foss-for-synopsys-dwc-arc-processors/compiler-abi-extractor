# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

.data
.globl regs_bank0
regs_bank0:
    .rept 32
    .word 0
    .endr

.text
.align  1
.globl  callee
.globl  get_stack_pointer
.type   callee, @function
callee:
    # Save t6 to the stack
    sw t6, -4(sp)

    # Initialize t6 to point to the start of the regs_bank0 array
    la t6, regs_bank0
    sw x0, 0(t6)
    sw x1, 4(t6)
    sw x2, 8(t6)
    sw x3, 12(t6)
    sw x4, 16(t6)
    sw x5, 20(t6)
    sw x6, 24(t6)
    sw x7, 28(t6)
    sw x8, 32(t6)
    sw x9, 36(t6)
    sw x10, 40(t6)
    sw x11, 44(t6)
    sw x12, 48(t6)
    sw x13, 52(t6)
    sw x14, 56(t6)
    sw x15, 60(t6)
    sw x16, 64(t6)
    sw x17, 68(t6)
    sw x18, 72(t6)
    sw x19, 76(t6)
    sw x20, 80(t6)
    sw x21, 84(t6)
    sw x22, 88(t6)
    sw x23, 92(t6)
    sw x24, 96(t6)
    sw x25, 100(t6)
    sw x26, 104(t6)
    sw x27, 108(t6)
    sw x28, 112(t6)
    sw x29, 116(t6)
    sw x30, 120(t6)

    # handle t6/x31
    lw x30, -4(sp)
    sw x30, 124(t6)
    lw x30, 120(t6)
    # Note: t6 register itself (x31) is not stored to regs_bank0 array

    # call to dump_information
    mv x10, sp
    call dump_information

    .size callee, .-callee

get_stack_pointer:
    mv a0, sp
    ret
