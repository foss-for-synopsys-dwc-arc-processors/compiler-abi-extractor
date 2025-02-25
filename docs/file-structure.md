### File Structure

This document outlines the framework's file structure, describing the organization and purpose of each file and directory.

# TODO

#### `lib/` Directory:
Contains scripts for analyzers, test generation, and various utilities
```bash
- `argPassTests.py` - Parses and generates summaries for Argument Passing test cases.
- `argPassTestsGen.py` - Generates C code for Argument Passing test cases.
- `bitFieldTests.py` - Parses and generates summaries for Bit Field test cases.
- `bitFieldGen.py` - Generates C code for Bit Field test cases.
- `datatypesTests.py` - Parses and generates summaries for Datatype test cases.
- `datatypesGen.py` - Generates C code for Datatype test cases.
- `emptyStructTests.py` - Parses and generates summaries for Empty Struct Argument Passing test cases.
- `emptyStructGen.py` - Generates C code for Empty Struct Argument Passing test cases.
- `returnTests.py` - Parses and generates summaries for Return Argument test cases.
- `returnGen.py` - Generates C code for Return Argument test cases.
- `savedTests.py` - Parses and generates summaries for Caller/Callee-Saved test cases.
- `savedGen.py` - Generates C code for Caller/Callee-Saved test cases.
- `structTests.py` - Parses and generates summaries for Struct Argument Passing test cases.
- `structGen.py` - Generates C code for Struct Argument Passing test cases.
- `stackAlignTests.py` - Generates C code for Stack Alignment test cases.
- `reportDriver` - Handles final report generation.
- `hexUtils` - Provides hexadecimal utilities.
- `helper.py` - Contains helper functions.
- `compilationDriver.py` - Manages compilation, assembling, linking, and simulation/emulation.
- `dumpInformation.py` - Parses architecture dump information.
- `targetArch.py` - Stores target architecture information.
```

#### `scripts/` Directory:
```bash
- `wrapper/cc/` - Contains wrappers for compilation, assembling, and linking.
- `wrapper/sim/` - Contains wrappers for simulation/emulation.
```

#### `src/` Directory:
```bash
- `arch/` - Contains assembly source code for architecture dump information.
- `endianness/` - Contains the C source code for the Endianness test case.
- `stack_dir/` - Contains the C source code for the Stack Direction test case.
- `helper.c` - C source code for architecture dump information.
```

### `tmp/` Directory
Stores temporary files generated during execution.
