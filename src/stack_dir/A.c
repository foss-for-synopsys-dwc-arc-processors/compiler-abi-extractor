/*
 * Copyright 2025-present, Synopsys, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the GPL-3.0 license found in
 * the LICENSE file in the root directory of this source tree.
 *
 */

#include "A.h"
#include "B.h"

// Declare global_addr_A as extern
extern void *global_addr_A;

void A() {
    int local_A;
    global_addr_A = (void *)&local_A;
    B();
}
