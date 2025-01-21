
# ABI Compatibility Toolset

This repository tracks the development of a toolset capable of validating that different RISC-V compilers follow the same ABI convention. Running the testsuites allow to identify where a particular compiler deviates from the ABI.


## abi-extract-info
This tool extracts the ABI from a compiler for a specified architecture and generates a summary report.

For out-of-the-box usage, please execute the "run" executable located in the "scripts" folder:
```bash
$ ./abi-extract-info/scripts/run
```

All files are generated in the "abi-extract-info/tmp" folder, which serves as the destination for generated and temporary files.

