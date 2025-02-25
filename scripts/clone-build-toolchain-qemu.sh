#!/usr/bin/env bash
# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

# This script clones and builds the RISC-V GNU Toolchain and QEMU.
#
# What it does:
# - Clones the RISC-V GNU Toolchain repository: https://github.com/riscv/riscv-gnu-toolchain.git
# - Configures, clones (via git submodules) and builds the following tools for 32-bit multilib:
#   - GCC (GNU Compiler Collection): https://gcc.gnu.org/git/gcc.git
#   - Binutils (Assembler, linker, and related tools): https://sourceware.org/git/binutils-gdb.git
#   - GDB (GNU Debugger): https://sourceware.org/git/binutils-gdb.git
#   - Newlib (C library for embedded systems): https://sourceware.org/git/newlib-cygwin.git
#   - QEMU (Emulator for running RISC-V binaries): https://gitlab.com/qemu-project/qemu.git
# - Sets up environment variables to use the built Toolchain and QEMU.
#
# Directory Structure:
# - The script creates the following directories in the folder where it is executed.
#   - toolchain/: Root directory for the workspace.
#   - toolchain/bld/: Build directory where compilation happens.
#   - toolchain/inst/: Installation directory for the Toolchain and QEMU binaries.
#
# What it does NOT do:
# - Install system dependencies required for the build (refer to the Toolchain and QEMU repositories for details)
#   - RISC-V GNU Toolchain: https://github.com/riscv/riscv-gnu-toolchain.git
#   - QEMU: https://gitlab.com/qemu-project/qemu
# - Verify existing installations or clean up previous builds.
#
# Prerequisites:
# - Git, make, and other dependencies required by riscv-gnu-toolchain and qemu.
# - Sufficient disk space.
#   - 2.2G for the installation directory (toolchain/inst/).
#   - 11.8G for build files (toolchain/bld).

set -eux

# Create a toolchain directory.
mkdir -p toolchain
pushd toolchain

# Clone the repository.
git clone https://github.com/riscv/riscv-gnu-toolchain.git --depth 1 --single-branch

# Create a build directory and configure the toolchain.
mkdir -p bld
pushd bld
../riscv-gnu-toolchain/configure --prefix="$(pwd)/../inst/" --with-arch=rv32gc --enable-multilib --disable-linux

# Building the RISC-V GCC GNU Toolchain.
# Check the repository for package dependencies: https://github.com/riscv-collab/riscv-gnu-toolchain
make newlib -j$(nproc)

# Building the RISC-V QEMU.
# Check the repository for package dependencies: https://gitlab.com/qemu-project/qemu
make build-qemu -j$(nproc)

# Return to the toolchain directory.
popd

# Configure the environment.
export PATH="$(pwd)/inst/bin:$PATH"

# Return to original directory.
popd

which riscv32-unknown-elf-gcc
which qemu-riscv32
