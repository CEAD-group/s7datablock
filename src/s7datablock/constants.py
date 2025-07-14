"""Constants and type definitions for S7 PLC data types."""
from datetime import datetime, time, timedelta
from typing import Final, Literal, TypeAlias, Union

# S7 Type Literals
S7ElementaryType = Literal[
    "Bool",
    "Byte",
    "Word",
    "DWord",
    "SInt",
    "USInt",
    "Int",
    "UInt",
    "DInt",
    "UDInt",
    "LInt",
    "ULInt",
    "Real",
    "LReal",
    "Char",
    "WChar",
]

S7DateTimeType = Literal[
    "S5Time",
    "Time",
    "LTime",
    "Date",
    "Time_of_Day",
    "DATE_AND_TIME",
    "LDT",
    "DTL",
    "LTIME_OF_DAY",
]

S7CompositeType = Literal["Struct"]
S7Type = Union[S7ElementaryType, S7DateTimeType, S7CompositeType]

# Type Aliases for values
S7ElementaryValue: TypeAlias = Union[bool, int, float, str]
S7DateTimeValue: TypeAlias = Union[datetime, time, timedelta, None]  # None for invalid/unset dates
S7Value: TypeAlias = Union[S7ElementaryValue, S7DateTimeValue]


# Sets of types
S7_ELEMENTARY_TYPES: Final = frozenset(
    [
        "Bool",
        "Byte",
        "Word",
        "DWord",
        "SInt",
        "USInt",
        "Int",
        "UInt",
        "DInt",
        "UDInt",
        "LInt",
        "ULInt",
        "Real",
        "LReal",
        "Char",
        "WChar",
    ]
)

S7_DATETIME_TYPES: Final = frozenset(
    ["S5Time", "Time", "LTime", "Date", "Time_of_Day", "DATE_AND_TIME", "LDT", "DTL", "LTIME_OF_DAY"]
)

S7_COMPOSITE_TYPES: Final = frozenset(["Struct"])
S7_ALL_TYPES: Final = S7_ELEMENTARY_TYPES | S7_DATETIME_TYPES | S7_COMPOSITE_TYPES

# Struct format mapping
S7_TYPE_TO_STRUCT_FORMAT: Final = {
    "Bool": "H",  # 1 byte, but packed as part of a word
    "Byte": "B",  # 8-bit unsigned
    "USInt": "B",  # 8-bit unsigned
    "Char": "c",  # 1 character, 1 byte
    "SInt": "b",  # 8-bit signed
    "UInt": "H",  # 16-bit unsigned
    "Word": "H",  # 16-bit unsigned
    "Int": "h",  # 16-bit signed
    "DInt": "i",  # 32-bit signed
    "UDInt": "I",  # 32-bit unsigned
    "DWord": "I",  # 32-bit unsigned
    "Real": "f",  # 32-bit IEEE 754 float
    "LReal": "d",  # 64-bit IEEE 754 float
    "Time": "I",  # 32-bit unsigned (milliseconds)
    "Date": "H",  # 16-bit unsigned (days since 1990-01-01)
    "Time_of_Day": "I",  # 32-bit unsigned (ms since midnight)
}
