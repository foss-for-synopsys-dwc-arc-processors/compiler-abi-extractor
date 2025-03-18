# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

import analyzer
import helper
import hexUtils
import dumpInformation

from analyzers.empty_struct import EmptyStructAnalyzer

"""
The purpose of this generator is to create a C test case that validates the
struct size boundaries during argument passing before being passed by
reference on the stack.

Given a list of data types, it generates a struct that is passed to an
external `callee()` function, which is responsible for dumping the register
and stack values.
"""


class StructGenerator:
    def __init__(self, Target, count, dtypes):
        self._result = []
        self.Target = Target
        self._count = count
        self.dtypes = dtypes

    def append(self, W):
        self._result.append(W)

    def get_result(self):
        return "\n".join(self._result)

    def generate_include(self):
        self.append("#include <stdio.h>")
        self.append("#include <string.h>")

    def generate_as_float(self):
        self.append(
            """
inline static float ul_as_float(unsigned long lhs)
{
    float result;
    memcpy(&result, &lhs, sizeof(float));
    return result;
}
"""
        )

    def generate_as_double(self):
        self.append(
            """
inline static double ull_as_double(unsigned long long lhs)
{
    double result;
    memcpy(&result, &lhs, sizeof(double));
    return result;
}
"""
        )

    def generate_converter(self):
        if "float" in self.dtypes:
            self.generate_as_float()
        if "double" in self.dtypes:
            self.generate_as_double()

    def generate_single_call_declare(self):
        declare_str = [
            f"    {dtype} a{i + 1};" for i, dtype in enumerate(self.dtypes)
        ]
        declare_str = "\n".join(declare_str)
        self.append(
            """
struct structType {
%s
};
"""
            % (declare_str)
        )

    def generate_single_call_prototypes(self):
        self.append("extern void callee(struct structType);")
        self.append("extern void reset_registers();")

    def generate_single_call_main(self, hvalues):
        hvalues_str = []
        for index, dtype in enumerate(self.dtypes):
            if dtype == "float":
                hvalues_str.append(f"ul_as_float({hvalues[index]})")
            elif dtype == "double":
                hvalues_str.append(f"ull_as_double({hvalues[index]})")
            else:
                hvalues_str.append(hvalues[index])
        self.append(
            """
int main (void) {
    printf("Sizeof(struct structType): %%d\\n", sizeof(struct structType));
    reset_registers();
    struct structType structTypeObject = { %s };
    callee(structTypeObject);

    return 0;
}
"""
            % (", ".join(hvalues_str))
        )

    def generate_single_call(self, hvalues):
        self.generate_include()
        self.generate_converter()
        self.generate_single_call_declare()
        self.generate_single_call_prototypes()
        self.generate_single_call_main(hvalues)

        return self.get_result()


"""
This class validates how arguments are passed within structs by checking
if a value appears in registers, the stack, or if its passed by reference.
"""


class StructTests:
    def __init__(self, Target):
        self.Target = Target

    # Process the results to categorize them according to their registers
    # and if values were splitted in pairs.
    def process_results(self, results):
        types = []
        passed_by_ref = {}
        boundaries = {}

        for dtype, iterations in results.items():
            # Floating-point registers in RISC-V are 64-bit in size,
            # so we cannot consider the size of an int. If an int is 32-bit,
            # it would split the value, which is incorrect the double data type.
            register_bank_count = self.Target.get_register_bank_count()
            if dtype == "double" and register_bank_count == 2:
                register_size = self.Target.get_register_size("regs_bank1")
            else:
                register_size = self.Target.get_register_size("regs_bank0")

            if len(iterations) > 1:
                iteration = iterations[-2]

                # Get the size of the current datatype
                sizeof_dtype = self.Target.get_type_details(dtype)["size"]

                if not types:
                    if sizeof_dtype == register_size:
                        types.append(
                            {
                                "sizeof(S)": iteration["sizeof(S)"],
                                "dtypes": [dtype],
                                "regs": list(
                                    iteration["registers_fill"].keys()
                                ),
                                "pairs": "",
                            }
                        )
                    elif sizeof_dtype < register_size:
                        types.append(
                            {
                                "sizeof(S)": iteration["sizeof(S)"],
                                "dtypes": [dtype],
                                "regs": list(
                                    iteration["registers_combined"].keys()
                                ),
                                "pairs": "",
                            }
                        )
                    elif sizeof_dtype > register_size:
                        types.append(
                            {
                                "sizeof(S)": iteration["sizeof(S)"],
                                "dtypes": [dtype],
                                "regs": list(
                                    iteration["registers_pairs"].keys()
                                ),
                                "pairs": iteration["pairs_order"],
                            }
                        )
                    continue

                # Get the registers according to the size type.
                if sizeof_dtype == register_size:
                    regs = list(iteration["registers_fill"].keys())
                elif sizeof_dtype < register_size:
                    regs = list(iteration["registers_combined"].keys())
                elif sizeof_dtype > register_size:
                    regs = list(iteration["registers_pairs"].keys())
                pairs = iteration["pairs_order"]

                found = False
                for x in types.copy():
                    # Aggregate the dtype according to their registers
                    # used and if they are in pairs.
                    if (
                        regs == x["regs"]
                        and pairs == x["pairs"]
                        and iteration["sizeof(S)"] == x["sizeof(S)"]
                    ):
                        x["dtypes"].append(dtype)
                        found = True
                        break

                if not found:
                    types.append(
                        {
                            "sizeof(S)": iteration["sizeof(S)"],
                            "dtypes": [dtype],
                            "regs": regs,
                            "pairs": pairs,
                        }
                    )

            # Check if there are at least two iterations
            if len(iterations) >= 2:
                second_last_iter = iterations[-2]
                last_iter = iterations[-1]

                # Track the boundary values based on the sizeof(S) for the second last iteration
                sizeof_S = second_last_iter["sizeof(S)"]
                boundaries.setdefault(sizeof_S, []).append(dtype)

                # Record the passed_by_ref status for the last iteration
                passed_by_ref[last_iter["passed_by_ref"]] = ""

        # Get the voundary value and the pass-by-ref value.
        passed_by_ref_value = next(iter(passed_by_ref.keys()), None)

        return types, boundaries, passed_by_ref_value

    def process_special_case(self, results):
        res = {}
        # Iterate through each dtype and corresponding iterations
        for dtype, iterations in results.items():
            dtype_str = dtype.replace("_", ",")

            # Determine the limit
            iterations_length = len(iterations)
            if (
                iterations[-1].get("passed_by_ref")
                and iterations_length >= 2
                and not iterations[-2]["passed_by_ref"]
            ):
                limit = len(iterations[-2]["dtypes,hvalues"])
            else:
                limit = 0

            limit_str = str(limit)

            # Initialize the data structure if not already present
            if limit_str not in res:
                res[limit_str] = {"<=": "", ">": "", "dtypes": []}

            # Access res[limit_str] once
            data = res[limit_str]

            # Process each iteration
            for iteration in iterations:
                argc = len(iteration["dtypes,hvalues"])

                # Handle dtypes and conditionally update "<=" and ">"
                if argc <= limit:
                    if dtype_str not in data["dtypes"]:
                        data["dtypes"].append(dtype_str)
                    if (
                        iteration["registers_fill"]
                        or iteration["registers_combined"]
                        or iteration["registers_pairs"]
                    ):
                        data["<="] = "in registers"
                    else:
                        data["<="] = "unknown"
                else:
                    if dtype_str not in data["dtypes"]:
                        data["dtypes"].append(dtype_str)
                    data[">"] = f"by ref: {iteration['passed_by_ref']}"

            # Second loop to check for matches if limit_str already exists
            if limit_str in res:
                for iteration in iterations:
                    argc = len(iteration["dtypes,hvalues"])
                    match = False

                    if argc <= limit:
                        if (
                            iteration["registers_fill"]
                            or iteration["registers_combined"]
                            or iteration["registers_pairs"]
                        ):
                            if data["<="] == "in registers":
                                match = True
                    else:
                        if data[">"] == f"by ref: {iteration['passed_by_ref']}":
                            match = True

                    if match and dtype_str not in data["dtypes"]:
                        data["dtypes"].append(dtype_str)

        return res

    def summary_results_special_case(self, res):
        summary = []
        for limit, data in res.items():
            if len(data["dtypes"]) != 4:
                break
            summary.append(f"- argc <= {limit} : passed {data['<=']}")
            summary.append(f"- argc >  {limit} : passed {data['>']}")
            dtypes_str = " : ".join(data["dtypes"])
            summary.append(f"  - {dtypes_str}")
        summary.append("")
        return summary

    # Create a summary
    def summary_results(self, types, boundaries, passed_by_ref_value):
        types_dict = {}
        for type_ in types:
            sizeof = type_["sizeof(S)"]
            types_dict.setdefault(sizeof, []).append(type_)

        summary = ["Struct argument passing test:"]
        for sizeof, types in types_dict.items():
            summary.append(f"- sizeof(S) <= {sizeof} : passed in registers")
            summary.append(
                f"- sizeof(S) >  {sizeof} : passed by ref: {passed_by_ref_value}"
            )

            for i in types:
                dtypes_str = " : ".join(i["dtypes"])
                regs_str = ", ".join(i["regs"])
                pairs_str = i["pairs"]
                summary.append(f"  - {dtypes_str} {pairs_str}: {regs_str}")
        summary.append("")
        return summary

    # Prepare the summary based on the test case results.
    def prepare_summary(self, results):
        # process the results
        types, boundaries, passed_by_ref_value = self.process_results(results)

        # Summarize and output the results
        summary = self.summary_results(types, boundaries, passed_by_ref_value)
        return "\n".join(summary)

    def prepare_summary_special_case(self, results):
        # Process the results
        res = self.process_special_case(results)

        # Summary and output the results
        summary = self.summary_results_special_case(res)
        return "\n".join(summary)

    # Run the test to check if the value is in registers or the stack.
    def run_test(self, citeration, dtype, stack, register_banks, argv):
        hutils = hexUtils.HexUtils(self.Target)

        # Check if the value is in the registers and update current test
        tmp = hutils.find_ref_in_stack_fill(
            dtype, argv.copy(), register_banks, stack
        )
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration

        tmp = hutils.find_ref_in_stack_pairs(
            dtype, argv.copy(), register_banks, stack
        )
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration

        tmp = hutils.find_ref_in_stack_combined(
            dtype, argv.copy(), register_banks, stack
        )
        citeration["passed_by_ref"], citeration["passed_by_ref_register"] = tmp
        if citeration["passed_by_ref"]:
            return citeration

        tmp = hutils.find_registers_fill(argv.copy(), register_banks)
        citeration["registers_fill"], _ = tmp

        tmp = hutils.find_registers_pairs(argv.copy(), register_banks)
        citeration["registers_pairs"], _, citeration["pairs_order"] = tmp

        tmp = hutils.find_registers_combined(argv.copy(), register_banks)
        citeration["registers_combined"], _ = tmp

        return citeration


class StructBoundaryAnalyzerSpecialCase(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "struct_boundary_special_case")

    def analyze(self):
        struct_tests = StructTests(self.Target)

        # As per the RISC-V ABi:
        # "A struct containing two floating-point reals is passed in two
        #  floating-point registers, if neither real is more than ABI_FLEN
        #   bits wide and at least two floating-registers are available."
        # To handle this, a special case is necessary to validate that the following
        # data type pairs are the struct boundary size limits:
        #   - float/double
        #   - double/float
        #   - float/float
        #   - double/double
        sc_results = {}
        special_cases = [
            ["float", "double"],
            ["double", "float"],
            ["float", "float"],
            ["double", "double"],
        ]
        for dtypes in special_cases:
            dtypes_str = "_".join(dtypes)
            sc_results[dtypes_str] = []
            for index, i in enumerate([[], ["char"]]):

                dtypes = dtypes + i
                hvalues = helper.generate_hexa_list_from_datatypes(
                    dtypes, self.Target
                )

                stdout = self.generate(
                    StructGenerator(
                        self.Target, None, dtypes
                    ).generate_single_call(hvalues)
                )

                # Parse the dump information.
                dump_information = dumpInformation.DumpInformation()
                dump_information.parse(stdout)

                # Get stack and register bank information
                stack = dump_information.get_stack()
                reg_banks = dump_information.get_reg_banks()

                # Regular expression to match the size
                regex = r"Sizeof\(struct structType\): (\d+)"
                size = helper.parse_regex(regex, stdout)

                citeration = {}
                citeration["sizeof(S)"] = size

                # Create tuple list of data type and the corresponding hexadecimal
                # values.
                tmp = [
                    (dtype, hvalues[index])
                    for index, dtype in enumerate(dtypes)
                ]
                citeration["dtypes,hvalues"] = tmp

                # FIXME The use of "double" is not correct, but it doesn't seem to
                # make any difference here.
                struct_tests.run_test(
                    citeration, "double", stack, reg_banks, hvalues
                )
                sc_results[dtypes_str].append(citeration)
                if citeration["passed_by_ref"] != None:
                    break

        return struct_tests.prepare_summary_special_case(sc_results)


class StructBoundaryAnalyzer(analyzer.Analyzer):
    def __init__(self, Driver, Report, Target):
        super().__init__(Driver, Report, Target, "struct_boundary")

    def analyze_char_limit(self, results):
        # The `char_limit` is calculated with the `char` datatype.
        # The test case will generate multiple C files to test the struct
        # boundaries, char by char. Once it reaches the stack as reference,
        # the `char_limit` is defined.
        # Start the char limit count with 1.
        char_limit = 1

        dtype = "char"
        results[dtype] = []
        char_sizeof = self.Target.get_type_details(dtype)["size"]

        # Reset the used generated values.
        helper.reset_used_values()
        while True:
            # Generate a hexadecimal value list according to the current count.
            hvalues = helper.generate_hexa_list(char_limit, char_sizeof)

            # Generate and build/execute the test case.
            dtypes = [dtype] * char_limit
            stdout = self.generate(
                StructGenerator(
                    self.Target, char_limit, dtypes
                ).generate_single_call(hvalues)
            )

            struct_tests = StructTests(self.Target)

            # Parse the dump information.
            dump_information = dumpInformation.DumpInformation()
            dump_information.parse(stdout)

            # Get stack and register bank information.
            stack = dump_information.get_stack()
            reg_banks = dump_information.get_reg_banks()

            # Extract the struct sizeof from C test case.
            # Regular expression to match the size
            regex = r"Sizeof\(struct structType\): (\d+)"
            size = helper.parse_regex(regex, stdout)

            citeration = {}
            citeration["sizeof(S)"] = size
            struct_tests.run_test(citeration, dtype, stack, reg_banks, hvalues)
            results[dtype].append(citeration)
            if citeration["passed_by_ref"] != None:
                break

            # The struct has not been passed by reference yet, so increment
            # the char limit by one.
            char_limit += 1
            if char_limit == 20:
                print("breaking for safe purposes [struct_boundaries]")
                break

        # Set back to the char's limit as its currently out of bounds.
        return char_limit - 1

    def analyze_struct_types(self, results, char_limit):
        struct_tests = StructTests(self.Target)

        # `long double` needs a different treating because its size
        # can be 16 bytes in a 32-bit architecture. That means that
        # the values are splitten in 4, and so that implementation
        # is yet to be added. FIXME
        types = ["short", "int", "long", "long long", "float", "double"]

        # HACK: This value will be replaced by a architecture validation
        # in the beginning of the framework execution.
        register_bank_count = 0

        for dtype in types:
            results[dtype] = []

            # Get datatype size from stored information from previous test case.
            sizeof_dtype = self.Target.get_type_details(dtype)["size"]

            # Calculate max datatype boundary according to sizeof.
            limit_dtype = char_limit // sizeof_dtype

            # The expected boundary may not be reached with the previously
            # calculated limit. In that case, we increment the limit_dtype by 1
            # and recalculate for the given data type. A maximum of 10 iterations
            # is enforced to prevent infinite loops.
            reached_boundary = False
            while not reached_boundary and limit_dtype < 10:
                # Generate the struct hexadecimal values with a list of data types.
                # Plus one char to validate the limit.
                for index, i in enumerate([[], ["char"]]):
                    dtypes = [dtype] * limit_dtype + i
                    hvalues = helper.generate_hexa_list_from_datatypes(
                        dtypes, self.Target
                    )
                    # Generate and build/execute the test case.
                    stdout = self.generate(
                        StructGenerator(
                            self.Target, None, dtypes
                        ).generate_single_call(hvalues)
                    )

                    # Parse the dump information.
                    dump_information = dumpInformation.DumpInformation()
                    dump_information.parse(stdout)

                    # Get stack and register bank information
                    stack = dump_information.get_stack()
                    reg_banks = dump_information.get_reg_banks()
                    # Get the register bank count from the header dump information.
                    register_bank_count = dump_information.get_reg_bank_count()

                    # Extract the struct sizeof from C test case.
                    # Regular expression to match the size
                    regex = r"Sizeof\(struct structType\): (\d+)"
                    size = helper.parse_regex(regex, stdout)

                    citeration = {}
                    citeration["sizeof(S)"] = size
                    struct_tests.run_test(
                        citeration, dtype, stack, reg_banks, hvalues
                    )
                    results[dtype].append(citeration)
                    if citeration["passed_by_ref"] != None:
                        reached_boundary = True
                        break
                limit_dtype = limit_dtype + 1

        # Store the register bank count.
        self.Target.set_register_bank_count(register_bank_count)

    def analyze_struct_boundaries(self):
        results = {}
        char_limit = self.analyze_char_limit(results)
        # Reset used values.
        helper.reset_used_values()
        self.analyze_struct_types(results, char_limit)

        return StructTests(self.Target).prepare_summary(results)

    def analyze(self):
        content = self.analyze_struct_boundaries()

        content += StructBoundaryAnalyzerSpecialCase(
            self.Driver, self.Report, self.Target
        ).analyze()

        # Run the empty struct test case.
        content += EmptyStructAnalyzer(
            self.Driver, self.Report, self.Target
        ).analyze()

        return content
