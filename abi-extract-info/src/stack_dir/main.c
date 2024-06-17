/*
 * Copyright 2025-present, Synopsys, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the GPL-3.0 license found in
 * the LICENSE file in the root directory of this source tree.
 *
 */

#include <stdio.h>
#include "A.h"
#include "B.h"

/*
 * This test case is designed to determine the stack
 * direction by using two function calls. Function "A"
 * defines a local variable and tracks its address in a
 * global variable. Function "A" then calls "B", where
 * "B" also defines a local variable and tracks its
 * address in another global variable.
 *
 * This approach allows to determine the stack
 * direction: if the nested stack address is higher,
 * the stack grows upwards; if it is lower, the stack
 * grows downwards.
 *
 */

// Global variables to store addresses of local variables
void *global_addr_A;
void *global_addr_B;

int main(void) {
    A();

    printf("Stack direction test:\n");

    // Determine the direction of the stack growth
    if (global_addr_B > global_addr_A) {
        printf("- The stack grows upwards.\n");
    } else {
        printf("- The stack grows downwards.\n");
    }

    return 0;
}
