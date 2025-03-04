### File Structure

This document outlines the framework's file structure, describing the organization and purpose of each file and directory.

# TODO

#### `abi-extract-info/` Directory:

Contains the Python source of the `abi-extract-info` utility:

```bash
- `__main__.py`          - The main function. Configures the utility and invokes every analyzer.
- `analyzers/*.py`       - The implementations of every analyzer.
- `stackAlignTests.py`   - Generates C code for Stack Alignment test cases.
- `reportDriver`         - Handles final report generation.
- `hexUtils`             - Provides hexadecimal utilities.
- `helper.py`            - Contains helper functions.
- `compilationDriver.py` - Manages compilation, assembling, linking, and simulation/emulation.
- `dumpInformation.py`   - Parses architecture dump information.
- `targetArch.py`        - Stores target architecture information.
```

#### `scripts/` Directory:
```bash
- `wrapper/cc/`  - Contains wrappers for compilation, assembling, and linking.
- `wrapper/sim/` - Contains wrappers for simulation/emulation.
```

#### `src/` Directory:
```bash
- `arch/`       - Contains assembly source code for architecture dump information.
- `endianness/` - Contains the C source code for the Endianness test case.
- `stack_dir/`  - Contains the C source code for the Stack Direction test case.
- `helper.c`    - C source code for architecture dump information.
```

### `tmp/` Directory
Stores temporary files generated during execution.
