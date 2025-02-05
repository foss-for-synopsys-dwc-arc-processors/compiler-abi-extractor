# Compiler ABI Extractor

How to ensure that object files from two compilers are ABI compatible?

This tool is capable of extracting ABI properties for a compiler. This human readable summary can be compared to another version, be it a reference version or one created for a different compiler or with different options, exposing where compatibility problems can pop up.

## Prerequisites

### Compiler ABI Extractor
Ensure Python is installed on the system:
```bash
$ sudo apt-get install python3
```

### Installing Prebuilt Binaries

#### RISC-V GCC GNU Toolchain
Prebuilt binaries for the toolchain are available in the [releases](https://github.com/riscv-collab/riscv-gnu-toolchain/releases) section of the `riscv-gnu-toolchain` repository.

Find the RISC-V 32-bit ELF GCC file. For example: `riscv32-elf-ubuntu-22.04-gcc-nightly-2025.01.20-nightly.tar.xz`

```bash
$ cd $HOME
# Replace `2025.01.20` with the latest version if necessary.
$ wget https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2025.01.20/riscv32-elf-ubuntu-22.04-gcc-nightly-2025.01.20-nightly.tar.xz
$ tar -xvf riscv32-elf-ubuntu-22.04-gcc-nightly-2025.01.20-nightly.tar.xz

# Configure the environment:
$ export PATH=$HOME/riscv/bin:$PATH
$ export LD_LIBRARY_PATH=$HOME/riscv/lib:$LD_LIBRARY_PATH
$ which riscv32-unknown-elf-gcc
```

**These binaries support only the `ilp32d` ABI.**

#### QEMU
To install QEMU for `riscv32`, run:
```bash
$ sudo apt-get install qemu-user
$ which qemu-riscv32
```

### Building from Source

To set up quickly, run the `clone-build-toolchain-qemu.sh` script:
```bash
$ source abi-extract-info/scripts/clone-build-toolchain-qemu.sh
```

This script will **clone** the RISC-V GNU Toolchain repository, which will then **clone (via git submodules) and build** the following tools:
- GCC (GNU Compiler Collection): https://gcc.gnu.org/git/gcc.git
- Binutils (Assembler, linker, and related tools): https://sourceware.org/git/binutils-gdb.git
- GDB (GNU Debugger): https://sourceware.org/git/binutils-gdb.git
- Newlib (C library for embedded systems): https://sourceware.org/git/newlib-cygwin.git
- QEMU (Emulator for running RISC-V binaries): https://gitlab.com/qemu-project/qemu.git

Examine the script for detailed steps.

Check the [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) and [qemu](https://gitlab.com/qemu-project/qemu) repositories for package dependencies.

## Quick Start
To run the tool with default settings, use:

```bash
$ cd abi-extract-info
$ python3 abi-extract-info.py
Running gcc-riscv32 with qemu-riscv32...
Report file generated at gcc-riscv32_qemu-riscv32.report
```

By default, the tool expects a RISC-V 32-bit GCC compiler (`riscv32-unknown-elf-gcc`) and a QEMU emulator (`qemu-riscv32`) to be available on the system. It generates a summary report named after the compiler and simulator wrappers used.

For more options, refer to the helper manual with `--help`:

```bash
Usage python3 abi-extract-info.py [options]
Options:
  -cc <compiler wrapper>        Select the compiler.
  -sim <simulator wrapper>      Select the simulator.
  -v | --verbose                Print execution commands.
  --print-report                Print summary report upon conclusion.
  --save-temps                  Do not delete the temporary files from "tmp/" directory.
  --help                        Display this information.
  --help=cc                     Display available compiler options.
  --help=sim                    Display available simulator options.
```

To list available configurations, run:

```bash
$ python3 abi-extract-info.py --help=cc --help=sim
Available configurations for CC:
- gcc-riscv32
- clang-riscv32
Available configurations for SIM:
- qemu-riscv32
```

## Documentation

For additional resources, see the `docs/` folder.

