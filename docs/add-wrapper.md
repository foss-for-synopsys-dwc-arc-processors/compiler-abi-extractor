### Configuration Wrappers

Configuration wrappers are `bash` scripts that act as intermediaries between the tool and compilers or simulators. They define the necessary steps to properly set up and execute the compiler or simulator.

Wrapper configurations are stored in the `scripts/wrapper` directory:
```bash
$ tree scripts/wrapper/
scripts/wrapper/
├── cc
│   ├── clang-riscv32
│   │   ├── as-wrapper
│   │   ├── cc-wrapper
│   │   └── ld-wrapper
│   └── gcc-riscv32
│       ├── as-wrapper
│       ├── cc-wrapper
│       └── ld-wrapper
└── sim
    └── qemu-riscv32
        └── sim-wrapper
```


The `cc` directory contains wrappers for the compiler, assembler, and linker, while `sim` holds wrappers for simulators or emulators.

#### Adding a New Wrapper

To add a new wrapper, create a subdirectory inside `scripts/wrapper/cc`. This directory will be referenced when executing the tool.

For example, to add a wrapper for `gcc-rv32-ilp32d`:
```bash
$ mkdir scripts/wrapper/cc/gcc-rv32gc-ilp32d
```

Next, create wrapper scripts for the compiler, assembler, and linker using the following naming convention:
```bash
scripts/wrapper/cc/gcc-rv32gc-ilp32d/
    ├── as-wrapper
    ├── cc-wrapper
    └── ld-wrapper
```

Create the corresponding files:
```bash
$ cd scripts/wrapper/cc/gcc-rv32gc-ilp32d/
$ touch {cc,as,ld}-wrapper
```

Each wrapper (`cc-wrapper`, `as-wrapper`, `ld-wrapper`) should contain the appropriate commands for its respective compilation stage.

Example:
```bash
$ cat cc-wrapper
#!/bin/bash

riscv32-unknown-elf-gcc -march=rv32gc -mabi=ilp32d "$@"
```

```bash
$ cat as-wrapper
#!/bin/bash

riscv32-unknown-elf-gcc -march=rv32gc -mabi=ilp32d "$@"
```

```bash
$ cat ld-wrapper
#!/bin/bash

riscv32-unknown-elf-gcc -march=rv32gc -mabi=ilp32d "$@"
`````

The tool applies the `-O1` optimization flag by default for all compilers.

