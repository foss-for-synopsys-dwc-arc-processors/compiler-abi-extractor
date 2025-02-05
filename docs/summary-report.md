### Summary Report

This document provides an overview of the summary reports for each test case executed within the framework.

#### Data Type size/alignment test case:
```bash
Datatype size test:
- 1: char : signed char : unsigned char
- 2: short
- 4: int : long : void* : float
- 8: long long : double
- 16: long double

Datatype align test:
 - 1: char : signed char : unsigned char
 - 2: short
 - 4: int : long : void* : float
 - 8: long long : double
 - 16: long double
```

These test cases present the **size (in bytes)** of the fundamental C data types along with thier correspoding type identifiers.
For example,  **int**, **long**, **void\***, and **float** all share the same **size** and **alignment**

#### Data Type signedness test case:
```bash
Datatype signedness test:
 - signed char : short : int : long : long long : float : double : long double
```

This test case presents fundatamental C data types that are capable of representing **negative** (signed), **zero**, and **positive values**.


#### Data Type Struct size/alignment test:
```bash
Datatype struct size test:
 - 1: char : signed char : unsigned char
 - 2: short
 - 4: int : long : void : float
 - 8: long_long : double
 - 16: long double

Datatype struct align test:
 - 1: char : signed_char : unsigned_char
 - 2: short
 - 4: int : long : void : float
 - 8: long_long : double
 - 16: long double
```
These test cases present the **size (in bytes)** and **alignment (in bytes)** of structs encapsulating fundamental C data types, along with their corresponding **encapsulated type identifiers**.
For example, structs such as `struct { int x; }`, `struct { long x; }`, `struct { void\* x; }`, `struct { float x; }` all share the same size and alignment.

#### Data Type Union size/alignment test:
```bash
Datatype union size test:
 - 1: char : signed_char : unsigned_char
 - 2: short
 - 4: int : long : void : float
 - 8: long_long : double
 - 16: long double

Datatype union align test:
 - 1: char : signed_char : unsigned_char
 - 2: short
 - 4: int : long : void : float
 - 8: long_long : double
 - 16: long double
`````

These test cases present the **size (in bytes)** and **alignment (in bytes)** of unions encapsulating fundamental C datatypes, along with their corresponding **encapsulated type identifiers**.
For example, unions such as `union { int x; }`, `union { long x; }`, `union { void\* x; }`, and `union { float x; }` all share the same size and alignment.

#### Stack Direction test case:
```bash
Stack direction test:
- The stack grows downwards.
```
This test case determines the **growth direction** of the stack - whether it expands **downwards** (toward lower memory addresses) or **Upwards** (towards higher memory addresses).

#### Stack Alignment test case:
```bash
Stack alignment test:
- Number of least significant 0 bits: 4
- Stack is aligned to 16 bytes.
```
This test case determines the alignment of the stack which refers to the mininum address boundary on which the stack pointer is maintained. The alignment is devired from the **least significant zero bits** in the stack pointer address. For example, if the address ends in hour zero bits (```0b...0000```), the stack is aligned to **16 bytes**.

#### Argument Passing test case:
```bash
Argument passing test:
- char : short : int : long : float
 - args 1-8 : a0 a1 a2 a3 a4 a5 a6 a7
 - args 9   : [stack]
- long long : double
 - args 1-4 [low], [high]: [a0, a1] [a2, a3] [a4, a5] [a6, a7]
 - args 5   [low], [high]: [stack]
```

This test case verifies how function arguments are passed — either in registers or on the stack.
It reports the number of arguments (e.g., "args 1-8") that fit in registers before switching to stack-based passing.

For values split due to register size limitations, they are represented as **[low]** and **[high]**, where:
- **[low]** represents the least significant half of the value.
- **[high]** represents the most significant half.


#### Struct Argument Passing test case:
```bash
Struct argument passing test:
- sizeof(S) <= 8 : passed in registers
- sizeof(S) >  8 : passed by ref: [stack]
 - char : short : int : long : float : a0 , a1
 - long long : double [low], [high]: a0, a1
- empty struct is ignored by C Compiler.
```

This test case validates the size limit of a struct encapsulating unique data types until it is passed by reference on the stack.
It will present the size of the struct and the behavior according to the size (e.g, `sizeof(S) <= 8 : passed in registers`) and also the registers used for which data type. (e.g., `char : short : int : long : float : a0 , a1`)

Additionally, it verifies whether the C compiler ignores empty structs when passing arguments.

##### Special RISC-V test case:

According to the RISC-V ABI specifications for hardware floating-point:
- *“A struct containing two floating-point reals is passed in two floating-point registers, if neither real is more than ABI_FLEN bits wide and at least two floating-registers are available.*

This means that the following struct layouts will behave the same way, with an increase in the number of members (not related to the struct size) resulting in the struct being passed by reference on the stack:
- `struct { float x; float y; }`
- `struct { double x; double y; }`
- `struct { float x; double y; }`
- `struct { double x; float y; }`

To validate this behavior, a special test case has been developed:
```bash
Struct argument passing test:
...
- argc <= 2 : passed in registers
- argc >  2 : passed by ref: [stack]
  - float,float : double,double : float,double : double,float
...
```

#### Endianness test case:
```bash
Endianess test:
- Wrote (as ull): 0123456789abcdef
- Read (as char): efcdab8967452301
- This system is little-endian.
```

This test case verifies the endianness of the system by writing and reading data in a specific format.
- A 64-bit unsigned long long (ull) value is written to memory: `0123456789abcdef`
- The same value is read as a sequence of bytes (as `char`), resuling in: `efcdab8967452301`
This behavior indicates that the system is little-endian, as the least significant byte appears first in memory.

#### Caller/Callee-saved test case
```bash
Caller/callee-saved test:
- caller-saved s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11
- callee-saved t0, t1, t2, a0, a1, a2, a3, a4, a5, a6, a7, t3, t4, t5, t6
```
This test case determines which registers are caller-saved and which are callee-saved.
- **Caller-saved registers**: The caller is responsible for saving these registers before making a function call, as they may be overwritten by the callee.
- **Callee-saved registers**: The callee must save and restore these registers if it modfiies them during execution.


#### Return test case
```bash
Return registers:
- char : short : int : long : float
  - passed in registers: a0
- long long : double
  - passed in registers [low], [high]: [a0, a1]
```

This test case validates whether return values for different data types are passed through registers or the stack. It reports the specific registers used for returning values.

For values split due to register size limitations, they are represented as **[low]** and **[high]**, where:
- **[low]** represents the least significant half of the value.
- **[high]** represents the most significant half.

