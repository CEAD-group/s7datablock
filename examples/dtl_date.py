from datetime import datetime

from s7datablock.fields import S7Field
from s7datablock.utils import BufferMapping

"""Example showing basic usage of BufferMapping with various data types"""
buf = bytearray(16)
var_mapping = {
    "enableFlags.enable0": S7Field.create(0, "Bool", offset_bit=0),
    "enableFlags.enable1": S7Field.create(0, "Bool", offset_bit=1),
    "enableFlags.enable2": S7Field.create(0, "Bool", offset_bit=2),
    "datetime": S7Field.create(2, "DTL"),
    **S7Field.create(2, "DTL").subfields,
    "a_word": S7Field.create(14, "Word"),
}


# Create a BufferMapping instance
buffered_vars = BufferMapping(buf, var_mapping)


# Set and show enable1 (use full key, not subfield)
buffered_vars["enableFlags.enable1"] = True
print("Buffer after setting enable1 (hex):", " ".join(f"{b:02X}" for b in buffered_vars.buffer))

# Set and show datetime
now = datetime(2025, 2, 9, 10, 2, 5, 123)
buffered_vars["datetime"] = now
print("Buffer after setting datetime (hex):", " ".join(f"{b:02X}" for b in buffered_vars.buffer))

# Allow manipulation of DTL subfields
print("\nBefore MONTH change:", buffered_vars["datetime"])
buffered_vars["datetime.MONTH"] = 7  # Change month to July
print("After MONTH change:", buffered_vars["datetime"])

# Show that WEEKDAY is calculated and read-only
try:
    buffered_vars["datetime.WEEKDAY"] = 3  # This should fail
    print("Should not reach here!")
except ValueError as e:
    print("Cannot set WEEKDAY:", str(e))

# Show the hex buffer after all changes
print("\nFinal buffer (hex):", " ".join(f"{b:02X}" for b in buffered_vars.buffer))

# Display the full structure with values
print("\nFull structure:")
print(buffered_vars)

# Expected output simething like this:
#
# Full structure:
# ┏━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Name        ┃ Data type ┃ Offset ┃ Value               ┃
# ┡━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
# │ enableFlags │ Struct    │    0.0 │                     │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │     enable0 │ Bool      │    0.0 │ True                 │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │     enable1 │ Bool      │    0.1 │ False                 │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │     enable2 │ Bool      │    0.2 │ False                 │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │ datetime    │ DTL       │    2.0 │ 2025-07-09 10:02:05 │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │     YEAR        │ Word      │  912.0 │ 2025  │
# ├─────────────────┼───────────┼────────┼───┤
# │     MONTH       │ Byte      │  914.0 │ 7  │
# ├─────────────────┼───────────┼────────┼───┤
# │     DAY         │ Byte      │  915.0 │  9 │
# ├─────────────────┼───────────┼────────┼───┤
# │     WEEKDAY     │ Byte      │  916.0 │  ??  │
# ├─────────────────┼───────────┼────────┼───┤
# │     HOUR        │ Byte      │  917.0 │  10 │
# ├─────────────────┼───────────┼────────┼───┤
# │     MINUTE      │ Byte      │  918.0 │  02 │
# ├─────────────────┼───────────┼────────┼───┤
# │     SECOND      │ Byte      │  919.0 │  05 │
# ├─────────────────┼───────────┼────────┼───┤
# │     NANOSECOND  │ DWord     │  920.0 │ 123000 │
# ├─────────────┼───────────┼────────┼─────────────────────┤
# │ a_word      │ Word      │   14.0 │ 0                   │
# └─────────────┴───────────┴────────┴─────────────────────┘
