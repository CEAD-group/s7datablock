# S7DataBlock

- [S7DataBlock](#s7datablock)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Parsing Data Blocks](#parsing-data-blocks)
  - [Contributing and Issues](#contributing-and-issues)

## Introduction

> A Python library for parsing Siemens S7 PLC data blocks, in conjunction with Snap7.

`s7datablock` is a Python library designed to parse and interpret Siemens S7 PLC data blocks. It works in conjunction with the [python-snap7](https://github.com/gijzelaerr/python-snap7) library, providing a set of tools and utilities to read and write the bytes in a PLC datablock as structured data, using the DB definitions as exported from a TIA Portal project. This makes it easier for developers and engineers to work with Siemens S7 PLCs in their Python applications.

Instead of manually mapping bytes, the dataformat defined in Tia Portal can be used to generate the appropriate Python mapping. The configuration file can be kept separate from the code, making it easier to track versions and support complicated data structures.

## Installation

```bash
pip install s7datablock
```

### Parsing Data Blocks

In this example, we will demonstrate how to use the `s7datablock` library to parse and interpret Siemens S7 PLC data blocks.

First, we define a s7_1200_out user-defined type (UDT) and a data block in Structured Control Language (SCL). The UDT, named "s7_1200_out_udt", consists of five boolean variables and one integer variable. The data block, named "s7_1200_out", uses this UDT. This file was defined in and exported from Tia Portal, using the `generate source from blocks, including all dependent blocks` option.

```scl
# s7_1200_out.db
TYPE "s7_1200_out_udt"
VERSION : 0.1
   STRUCT
      PLC_DQ_0 : Bool;  # Boolean variable
      PLC_DQ_1 : Bool;  # Boolean variable
      PLC_DQ_2 : Bool;  # Boolean variable
      PLC_DQ_3 : Bool;  # Boolean variable
      PLC_DQ_4 : Bool;  # Boolean variable
      SB_AQ_0 : Int;    # Integer variable
   END_STRUCT;
END_TYPE

DATA_BLOCK "s7_1200_out"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
"s7_1200_out_udt"

BEGIN

END_DATA_BLOCK
```

Next, we use the `S7DataBlock` class from the `s7datablock` library to parse the data block definition file. We then display the parsed data block and its initial buffer state. Finally, we modify one of the boolean variables in the data block and display the updated buffer state.

```python
# Import necessary modules
from s7datablock.mapping import S7DataBlock
from pathlib import Path

# Parse the data block definition file
db1200 = S7DataBlock.from_definition_file(
    Path("tests/definitions/s7_1200_out.db"),
    db_number=1200
)

# The printing the db1200 datasrutcure produces a nicely formatted output
print(db1200)
```

```raw
                   Data Block Structure
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Name             ┃ Data type   ┃   Offset ┃ Value       ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ PLC_DQ_0         │ Bool        │      0.0 │ False       │
│ PLC_DQ_1         │ Bool        │      0.1 │ False       │
│ PLC_DQ_2         │ Bool        │      0.2 │ False       │
│ PLC_DQ_3         │ Bool        │      0.3 │ False       │
│ PLC_DQ_4         │ Bool        │      0.4 │ False       │
│ SB_AQ_0          │ Int         │      2.0 │ 0           │
│ TIMEFIELD        │ DTL         │      4.0 │ None        │
│   YEAR           │ UInt        │      4.0 │ 0           │
│   MONTH          │ USInt       │      6.0 │ 0           │
│   DAY            │ USInt       │      7.0 │ 0           │
│   WEEKDAY        │ USInt       │      8.0 │ 0           │
│   HOUR           │ USInt       │      9.0 │ 0           │
│   MINUTE         │ USInt       │     10.0 │ 0           │
│   SECOND         │ USInt       │     11.0 │ 0           │
│   NANOSECOND     │ UDInt       │     12.0 │ 0           │
└──────────────────┴─────────────┴──────────┴─────────────┘
             Total size: 16 bytes
```

```python
# db1200 maps the data like a dictionary but the hood it stores the data in a continuous buffer,
# using the same format and byte ordering as the PLC
# Initially the buffer is only zeros
print(db1200.buffer)
# Output: bytearray(b'\x00\x00\x00\x00')

# Modify one of the boolean variables
db1200["PLC_DQ_3"] = True

# Now one bit has changed
print(db1200.buffer)
# Output: bytearray(b'\x08\x00\x00\x00')
```



## Contributing and Issues

The library is in its early stages, and contributions are welcome. Feel free to submit a pull request or open an issue on GitHub.
