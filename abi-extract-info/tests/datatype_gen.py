
variables = [
        ("char", "x10"),
        ("char", "x11"),
        ("char", "a"),
        ("short", "b"),
        ("int", "c"),
        ("long", "d"),
        ("char", "x1"),
        ("long long", "e"),
        ("char", "x2"),
        ("float", "f"),
        ("char", "x3"),
        ("double", "g"),
        ("char", "x4"),
        ("long double", "h")
    ]

def generate_c_file ():
    print ("#include <stdio.h>")
    print ("#include <stdint.h>")
    print ("")
    
    for vtype, vname in variables:
        print (f"volatile {vtype} {vname};")
    print ("")
    
    print (
        "void\n"
        "print_info (void *a, size_t size, const char *datatype)\n"
        "{\n"
        "   uintptr_t address = (uintptr_t)a;\n"
        "   // Extracting the last four bits\n"
        "   int bit_0 = address & 1;\n"
        "   int bit_1 = (address >> 1) & 1;\n"
        "   int bit_2 = (address >> 2) & 1;\n"
        "   int bit_3 = (address >> 3) & 1;\n"
        "   printf(\".%s - size: %zu, align: %d%d%d%d\\n\", datatype, size, bit_3, bit_2, bit_1, bit_0);\n"
        "}\n"
    )

    print (
       "int\n"
       "main (void)\n"
       "{\n"
    )

    for _, vname in variables:
        if not vname.startswith("x"):
            print (f"  print_info(&{vname}, sizeof({vname}), \"{vtype}\");")
    print ("\n  return 0;\n}\n")

generate_c_file ()
