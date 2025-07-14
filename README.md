# S7DataBlock

- [S7DataBlock](#s7datablock)
  - [Key Features](#key-features)
  - [Data Transfer](#data-transfer)
  - [Live Monitoring PLC Values](#live-monitoring-plc-values)
  - [Installation](#installation)
  - [Contributing and Issues](#contributing-and-issues)

**A Python library for parsing Siemens S7 PLC data blocks, in conjunction with Snap7.**

`s7datablock` is a Python utility designed to parse and interpret Siemens S7 PLC data blocks using structured data definitions exported from the TIA Portal. It works seamlessly with the excellent [python-snap7](https://github.com/gijzelaerr/python-snap7) library to enable high-level, dictionary-like access to binary PLC data.

Instead of manually mapping byte offsets and types, you can use `.db` definition files exported from TIA Portal to generate a clean, versionable Python representation of your data block structures.

---

## Key Features

- Uses exported TIA Portal `*.db` files for accurate structure mapping
- Read and write entire PLC data blocks with `.GET()` and `.SET()` (or the more pythonic `pull()` and `push()`)
- Structure and sub-structure access via dot notation
- Clean terminal output using [Rich](https://github.com/Textualize/rich)
- Easy integration into polling and monitoring loops

![example.png](docs/example.png)

---

## Data Transfer

This library deliberately uses manual .GET() and .SET() calls instead of automatic syncing to prioritize:
 - **Clarity** – Developers control exactly when data is transferred
 - **Performance** – Avoid unnecessary communication overhead
 - **Atomicity** – Batch multiple updates into one write

## Live Monitoring PLC Values

You can monitor PLC values by creating a polling loop. Here's an example using Rich for clean terminal output:

```python
from time import sleep
from rich.live import Live
from datetime import datetime
from io import StringIO

from s7datablock.mapping import S7DataBlock

# Example in-line definition file contents. Alternatively, you can pass a PAth to a *.db file.
df_file_contents = StringIO(
    """
        TYPE "my_udt"
        VERSION : 0.1
        STRUCT
            PLC_DQ_0 : Bool;
            PLC_DQ_1 : Bool;
            WHEN : DTL;
            Value1 : Int;
            Value2 : Real;
        END_STRUCT;
        END_TYPE
        DATA_BLOCK "my_udt"
        VERSION : 0.1
        "my_udt"
        BEGIN
        END_DATA_BLOCK
    """
)

db = S7DataBlock.from_definition_file(df_file_contents, db_number=1200)
print(db) # This will print the structure of the data block as a table

# In a real application, you would create a snap7 client and connect to the PLC

# client = snap7.client.Client()
# client.connect('192.168.0.1', 0, 1)

with Live(db.to_table(), refresh_per_second=10) as live:
    while True:
        # In a real application, you would call GET() here
        # db.GET(client)

        # For demo, we'll just modify some values
        db["my_udt.WHEN"] = datetime.now()
        db["my_udt.PLC_DQ_0"] = not db["my_udt.PLC_DQ_0"]  # Toggle the boolean
        db["my_udt.Value1"] = db["my_udt.Value1"] + 1  # Increment the integer value
        db["my_udt.Value2"] = db["my_udt.Value2"] + 0.1  # Increment the real value

        # Update the display with current values
        live.update(db.to_table())
        sleep(0.2)
```

Running this code should render a live table in your terminal
```text

                            Data Block Structure
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                       ┃ Data type   ┃   Offset ┃ Value               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ my_udt                     │ Struct      │          │                     │
│   my_udt.PLC_DQ_0          │ Bool        │      0.0 │ False               │
│   my_udt.PLC_DQ_1          │ Bool        │      0.1 │ False               │
│   my_udt.WHEN              │ DTL         │      2.0 │ 2025-07-14 16:06:06 │
│     my_udt.WHEN.YEAR       │ UInt        │      2.0 │ 2025                │
│     my_udt.WHEN.MONTH      │ USInt       │      4.0 │ 7                   │
│     my_udt.WHEN.DAY        │ USInt       │      5.0 │ 14                  │
│     my_udt.WHEN.WEEKDAY    │ USInt       │      6.0 │ 1                   │
│     my_udt.WHEN.HOUR       │ USInt       │      7.0 │ 16                  │
│     my_udt.WHEN.MINUTE     │ USInt       │      8.0 │ 6                   │
│     my_udt.WHEN.SECOND     │ USInt       │      9.0 │ 6                   │
│     my_udt.WHEN.NANOSECOND │ UDInt       │     10.0 │ 195792000           │
│   my_udt.Value1            │ Int         │     14.0 │ 44                  │
│   my_udt.Value2            │ Real        │     16.0 │ 4.400               │
└────────────────────────────┴─────────────┴──────────┴─────────────────────┘
```



## Installation

```bash
pip install s7datablock
```


## Contributing and Issues

The library is in its early stages, and contributions are welcome. Feel free to submit a pull request or open an issue on GitHub.
