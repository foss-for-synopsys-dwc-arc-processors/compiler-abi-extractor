# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

# Print value at first position of the struct and pop it
.macro print_reg
    lw a1, 0(t6)
    lui a5, %hi(.LC0)
    addi a0, a5, %lo(.LC0)

    # The t6 register is used in the printf
    # function, so we need to save it otherwise the address
    # of the struct is lost
    addi sp, sp, -4
    sw t6, 0(sp)

    call printf

    # pop t6
    lw t6, 0(sp)
    addi sp, sp, 4

    addi t6, t6, 4
.endm

# Print value from the stack and pop it
.macro print_sp
    lw a1, 0(sp)
    lui a5, %hi(.LC0)
    addi a0, a5, %lo(.LC0)
    call printf
    addi sp, sp, 4
.endm

.data
regs:
    .rept 32
    .word 0
    .endr
.LC0:
    .string "0x%x\n"

.text
.align  1
.globl  callee
.globl  get_stack_pointer
.type   callee, @function
callee:
    # Save t6 to the stack
    addi sp, sp, -4
    sw t6, 0(sp)

    # Initialize t6 to point to the start of the regs array
    la t6, regs
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
    # Note: t6 register itself (x31) is not stored to regs array

    # Print all 31 registers
    .rept 31
    print_reg
    .endr

    # Print the saved t6 (register 31) value from the stack
    lw a1, 0(sp)
    lui a5, %hi(.LC0)
    addi a0, a5, %lo(.LC0)
    call printf
    addi sp, sp, 4

    # Print all 32 saved stack values (sp)
    .rept 32
    print_sp
    .endr

    # Exit
    addi a0, x0, 0
    addi a7, x0, 93
    ecall

    .size callee, .-callee

get_stack_pointer:
    mv a0, sp
    ret
