/*
 * Copyright 2025-present, Synopsys, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the GPL-3.0 license found in
 * the LICENSE file in the root directory of this source tree.
 *
 */

#include <stdio.h>

/*
 * This test case is designed to determine the endianness
 * of the current compiler. It leverages C unions to define
 * a long long integer value and subsequently examines the
 * contents of a char datatype.
 *
 * - It is determined to be little-endian if the first byte
 *   found is "ef".
 *
 * - It is determined to be big-endian if the first byte
 *   found is "01".
 *
 * TODO: mixed-endian.
 */

union Endian {
    unsigned long long int ll_value;
    unsigned char c_value;
};

int
main (void)
{
  // Define the union
  union Endian test;
  test.ll_value = 0x0123456789abcdef;

  // Check the first byte
  if (test.c_value == 0xef)
    printf("This system is little-endian.\n");
  else if (test.c_value == 0x01)
    printf("This system is big-endian.\n");
  else
    // TODO: Validate mixed endianness.
    printf("Endianness cannot be determined.\n");

  return 0;
}

