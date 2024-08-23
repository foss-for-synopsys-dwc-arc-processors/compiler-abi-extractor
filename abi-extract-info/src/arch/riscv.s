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
.globl  reset_registers
.globl  set_registers
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

    # save the callee-saved register
    sw s2, 8(sp)

    # save the return address to a callee-saved register
    lw s2, 4(t6)

    # call to dump_information
    mv x10, sp
    call dump_information

    # restore the return address
    addi ra, s2, 0

    # restore the calee-saved register
    lw s2, 8(sp)

    ret

    .size callee, .-callee

reset_registers:
    # cleanup: clear or reset registers
    li x5, 0  # t0
    li x6, 0  # t1
    li x7, 0  # t2
    li x10, 0 # a0
    li x11, 0 # a1
    li x12, 0 # a2
    li x13, 0 # a3
    li x14, 0 # a4
    li x15, 0 # a5
    li x16, 0 # a6
    li x17, 0 # a7
    li x28, 0 # t3
    li x29, 0 # t4
    li x30, 0 # t5
    li x31, 0 # t6
    ret

get_stack_pointer:
    mv a0, sp
    ret

set_registers:
    addi x5, a0, 0
    addi x6, a0, 0
    addi x7, a0, 0
    addi x8, a0, 0
    addi x9, a0, 0
    addi x10, a0, 0
    addi x11, a0, 0
    addi x12, a0, 0
    addi x13, a0, 0
    addi x14, a0, 0
    addi x15, a0, 0
    addi x16, a0, 0
    addi x17, a0, 0
    addi x18, a0, 0
    addi x19, a0, 0
    addi x20, a0, 0
    addi x21, a0, 0
    addi x22, a0, 0
    addi x23, a0, 0
    addi x24, a0, 0
    addi x25, a0, 0
    addi x26, a0, 0
    addi x27, a0, 0
    addi x28, a0, 0
    addi x29, a0, 0
    addi x30, a0, 0
    addi x31, a0, 0
    ret
