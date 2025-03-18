/*
 * Copyright 2025-present, Synopsys, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the GPL-3.0 license found in
 * the LICENSE file in the root directory of this source tree.
 *
 */

// Helper function for dumping informatino
#include <stdio.h>
#include <stdint.h>

#if __riscv_xlen == 64
#define REGISTER_WORD uint64_t
#define REGISTER_WORD_FORMAT "0x%llx\n"
#else
#define REGISTER_WORD uint32_t
#define REGISTER_WORD_FORMAT "0x%x\n"
#endif

extern REGISTER_WORD regs_bank0[32];
#ifndef __riscv_float_abi_soft
extern uint64_t regs_bank1[32];
#endif

#define ARRAY_LENGTH(x) sizeof(x)/sizeof(x[0])

void dump_information(REGISTER_WORD* Stack) {
    // current stack
    // sizeof pointer (aka register)
    printf("// Header info\n");
    printf("%p\n0x%08x\n", Stack, sizeof(Stack));
    // Number of register banks
#ifndef __riscv_float_abi_soft
    printf("0x2\n");
#else
    printf("0x1\n");
#endif
    // bank0:  ID, size, number of regs
    printf("%s\n0x%x\n0x%x\n",
           /*ID*/ "regs_bank0",
           sizeof(regs_bank0[0]),
           /*number of regs*/ ARRAY_LENGTH(regs_bank0));
#ifndef __riscv_float_abi_soft
    // bank1:  ID, size, number of regs
    printf("%s\n0x%x\n0x%x\n",
           /*ID*/ "regs_bank1",
           sizeof(regs_bank1[0]),
           /*number of regs*/ ARRAY_LENGTH(regs_bank1));
#endif

    // Dump register bank0: regs_bank0
    printf("// regs_bank0\n");
    for(unsigned i=0; i<ARRAY_LENGTH(regs_bank0); ++i)
       printf(REGISTER_WORD_FORMAT, regs_bank0[i]);

#ifndef __riscv_float_abi_soft
    // Dump register bank1: regs_bank1
    printf("// regs_bank1\n");
    for(unsigned i=0; i<ARRAY_LENGTH(regs_bank1); ++i)
       printf("0x%llx\n", regs_bank1[i]);
#endif

    // stack: 32 entries (128 bytes on 32bit system)
    printf("// Start of stack dump: %p\n", Stack);
    for(unsigned i=0; i<32; ++i){
        printf("%p : " REGISTER_WORD_FORMAT, &Stack[i], Stack[i]);
    }
    printf("// Done\n");
}
