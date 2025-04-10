# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

#if __riscv_xlen == 64
#define T6_STACK_OFFSET -8
#define S2_STACK_OFFSET -16
#else
#define T6_STACK_OFFSET -4
#define S2_STACK_OFFSET -8
#endif

.data
.globl regs_bank0
.globl regs_bank1

regs_bank0:
    .rept 32
    .dword 0
    .endr
    .size regs_bank0, .-regs_bank0

regs_bank1:
    .rept 32
    .dword 0
    .endr
    .size regs_bank1, .-regs_bank1

.text
.align  1
.globl  callee
.globl  get_stack_pointer
.globl  set_registers
.type   callee, @function
callee:
#if __riscv_xlen == 64
    # Save t6 to the stack
    sd t6, T6_STACK_OFFSET(sp)

    # Initialize t6 to point to the start of the regs_bank0 array
    la t6, regs_bank0
    sd x0, 0(t6)
    sd x1, 8(t6)
    sd x2, 16(t6)
    sd x3, 24(t6)
    sd x4, 32(t6)
    sd x5, 40(t6)
    sd x6, 48(t6)
    sd x7, 56(t6)
    sd x8, 64(t6)
    sd x9, 72(t6)
    sd x10, 80(t6)
    sd x11, 88(t6)
    sd x12, 96(t6)
    sd x13, 104(t6)
    sd x14, 112(t6)
    sd x15, 120(t6)
    sd x16, 128(t6)
    sd x17, 136(t6)
    sd x18, 144(t6)
    sd x19, 152(t6)
    sd x20, 160(t6)
    sd x21, 168(t6)
    sd x22, 176(t6)
    sd x23, 184(t6)
    sd x24, 192(t6)
    sd x25, 200(t6)
    sd x26, 208(t6)
    sd x27, 216(t6)
    sd x28, 224(t6)
    sd x29, 232(t6)
    sd x30, 240(t6)
#else
    # Save t6 to the stack
    sw t6, T6_STACK_OFFSET(sp)

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
#endif

    # Initialize t6 to point to the start of the regs_bank1 array
#ifndef __riscv_float_abi_soft
    la t6, regs_bank1
    fsd f0, 0(t6)
    fsd f1, 8(t6)
    fsd f2, 16(t6)
    fsd f3, 24(t6)
    fsd f4, 32(t6)
    fsd f5, 40(t6)
    fsd f6, 48(t6)
    fsd f7, 56(t6)
    fsd f8, 64(t6)
    fsd f9, 72(t6)
    fsd f10, 80(t6)
    fsd f11, 88(t6)
    fsd f12, 96(t6)
    fsd f13, 104(t6)
    fsd f14, 112(t6)
    fsd f15, 120(t6)
    fsd f16, 128(t6)
    fsd f17, 136(t6)
    fsd f18, 144(t6)
    fsd f19, 152(t6)
    fsd f20, 160(t6)
    fsd f21, 168(t6)
    fsd f22, 176(t6)
    fsd f23, 184(t6)
    fsd f24, 192(t6)
    fsd f25, 200(t6)
    fsd f26, 208(t6)
    fsd f27, 216(t6)
    fsd f28, 224(t6)
    fsd f29, 232(t6)
    fsd f30, 240(t6)
    fsd f31, 248(t6)
#endif
    la t6, regs_bank0

#if __riscv_xlen == 64
    # handle t6/x31
    ld x30, T6_STACK_OFFSET(sp)
    sd x30, 248(t6)
    ld x30, 240(t6)
    # Note: t6 register itself (x31) is not stored to regs_bank0 array

    # save the callee-saved register
    sd s2, S2_STACK_OFFSET(sp)

    # save the return address to a callee-saved register
    ld s2, 8(t6)

    # call to dump_information
    mv x10, sp
    call dump_information

    # restore the return address
    addi ra, s2, 0

    # restore the calee-saved register
    ld s2, S2_STACK_OFFSET(sp)
#else
    # handle t6/x31
    lw x30, T6_STACK_OFFSET(sp)
    sw x30, 124(t6)
    lw x30, 120(t6)
    # Note: t6 register itself (x31) is not stored to regs_bank0 array

    # save the callee-saved register
    sw s2, S2_STACK_OFFSET(sp)

    # save the return address to a callee-saved register
    lw s2, 4(t6)

    # call to dump_information
    mv x10, sp
    call dump_information

    # restore the return address
    addi ra, s2, 0

    # restore the calee-saved register
    lw s2, S2_STACK_OFFSET(sp)
#endif

    ret

    .size callee, .-callee

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
