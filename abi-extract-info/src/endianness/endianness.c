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
 */

union Endian {
  unsigned long long int ll_value;
  unsigned char c_value[sizeof(unsigned long long)];
};

int main (void) {
  const unsigned long long ref_value = 0x0123456789abcdef;
  const unsigned long long le_value  = 0xefcdab8967452301;
  const unsigned long long be_value  = 0x0123456789abcdef;

    // Define the union
  union Endian test;
  test.ll_value = ref_value;

  unsigned long long value = 0;
  for (int i=0; i<sizeof(unsigned long long); ++i) {
    value = (value << 8) | test.c_value[i];
  }

  // Check the first byte
  printf("Endianess test:\n");
  printf("- Wrote (as ull):  %016llx\n", ref_value);
  printf("- Read  (as char): %016llx\n", value);
  if (value == le_value)
    printf("- This system is little-endian.\n");
  else if (value == be_value)
    printf("- This system is big-endian.\n");
  else
    // TODO: Validate mixed endianness.
    printf("- This system is mixed-endianness.\n");

  return 0;
}

