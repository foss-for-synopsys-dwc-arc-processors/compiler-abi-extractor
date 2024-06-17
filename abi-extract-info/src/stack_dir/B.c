/*
 * Copyright 2025-present, Synopsys, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the GPL-3.0 license found in
 * the LICENSE file in the root directory of this source tree.
 *
 */

#include "B.h"

// Declare global_addr_B as extern
extern void *global_addr_B;

void B() {
    int local_B;
    global_addr_B = (void *)&local_B;
}
