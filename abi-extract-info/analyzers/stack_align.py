# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

N = [i for i in range(1, 65)]
# N = [i for i in range(1, 10) if i % 2 != 0]


class DriverGenerator:
    def __init__(self):
        self.Result = []

    def append(self, W):
        self.Result.append(W)

    def getResult(self):
        return "\n".join(self.Result)

    def generateBase(self):
        self.append("#include <stdio.h>")
        self.append("#include <stdint.h>")
        self.append('#include "out_functions.h"')
        self.append(
            """
/*
 * This test case calculates the alignment of the stack pointer at each
 * recursive call.
 * Each function TrackAlignment1 to TrackAlignment64 allocates a local array
 * of increasing size, from 1 to 64 bytes, simulating stack growth with
 * recursive function calls.
 *
 * The value of the stack pointer after each function call is tracked using
 * the assembly get_stack_pointer() function implementation, and stored
 * in.
 *
 * To determine the stack alignment in the main function, we count the
 * number of trailing zero bits in the tracked variable. This count represents
 * the number of bits the stack pointer is aligned to, which is equivalent
 * to the stack alignment in bytes.
 *
 * Note: By passing A to the dummy variable, we hide information from the
 * compiler to prevent optimization.
 */"""
        )

    def generateMain(self):
        self.append(
            """
int main() {
    p_functions_struct FunctionArray = {
        .functions = {"""
        )
        for n in N:
            self.append(f"            TrackAlignment{n},")

        self.append(
            """
        }
    };

    uintptr_t alignment = 0;

    int startIndex = sizeof(FunctionArray.functions) / sizeof(FunctionArray.functions[0]) - 1;
    FunctionArray.functions[startIndex](&alignment, &FunctionArray, startIndex, NULL);

    int finalAlignment = CalculateAlignment(alignment);

    printf("Stack alignment test:\\n");
    printf("- Number of least significant 0 bits: %d\\n", finalAlignment);
    printf("- Stack is aligned to %d bytes.\\n", 1 << finalAlignment);

    return 0;
}
"""
        )

    def generate(self):
        self.generateBase()
        self.generateMain()

        return self.getResult()


class FunctionsGenerator:
    def __init__(self):
        self.Result = []

    def append(self, W):
        self.Result.append(W)

    def getResult(self):
        return "\n".join(self.Result)

    def generateBase(self):
        self.append("#include <stdio.h>")
        self.append("#include <stdint.h>")
        self.append('#include "out_functions.h"')

    def generateFunctions(self):
        for n in N:
            self.append(
                """
void TrackAlignment%d(uintptr_t* p_Alignment, p_functions_struct* FunctionArray, int Index, void *Dummy) {
    char A[%d]; // N = %d
    *p_Alignment |=  get_stack_pointer();
    if (Index > 0) {
        FunctionArray->functions[Index-1](p_Alignment, FunctionArray, Index-1, &A[0]);
    }
}"""
                % (n, n, n)
            )

        self.append(
            """
int CalculateAlignment(uintptr_t alignment) {
    int count = 0;
    while ((alignment & 1) == 0) {
        alignment >>= 1;
        count++;
    }
    return count;
}

"""
        )

    def generate(self):
        self.generateBase()
        self.generateFunctions()
        return self.getResult()


class FunctionsHeaderGenerator:
    def __init__(self):
        self.Result = []

    def append(self, W):
        self.Result.append(W)

    def getResult(self):
        return "\n".join(self.Result)

    def generateBase(self):
        self.append("#ifndef FUNCTIONS_H")
        self.append("#define FUNCTIONS_H")
        self.append("#include <stdint.h>")

    def generateFunctionsHeader(self):
        self.append("struct p_functions_struct;")
        self.append(
            "typedef void (*p_function)(uintptr_t*, struct p_functions_struct*, int, void*);"
        )

        self.append(
            """
typedef struct p_functions_struct {
    p_function functions[%d];
} p_functions_struct;
"""
            % (len(N))
        )

        self.append("extern unsigned long get_stack_pointer(void);")
        for n in N:
            self.append(
                f"void TrackAlignment{n}(uintptr_t* p_Alignment, p_functions_struct* FunctionArray, int Index, void *Dummy);"
            )
        self.append("int CalculateAlignment(uintptr_t alignment);")
        self.append("#endif // FUNCTIONS_H")

    def generate(self):
        self.generateBase()
        self.generateFunctionsHeader()

        return self.getResult()


def do_stack_align(Driver, Report):
    Content = DriverGenerator().generate()
    open("tmp/out_driver.c", "w").write(Content)
    Content = FunctionsGenerator().generate()
    open("tmp/out_functions.c", "w").write(Content)
    Content = FunctionsHeaderGenerator().generate()
    open("tmp/out_functions.h", "w").write(Content)

    # `src/heler.c` has been added as a placeholder for the dump_information function
    # as it is called within the `callee` function in `src/arch/riscv.s`.
    # Although this function is not used, it is present in the riscv.s file.
    source_files = ["tmp/out_functions.c", "tmp/out_driver.c", "src/helper.c"]
    assembly_files = ["src/arch/riscv.S"]
    output_name = "out_stackalign"
    res, stdoutFile = Driver.run(source_files, assembly_files, output_name)
    if res != 0:
        print("Skip: Stack Alignment test case failed.")
        return
    Report.append(stdoutFile)
