"""S7Field definitions for S7 PLC data types."""
from __future__ import annotations

import struct
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Generic, NamedTuple, TypeVar, cast

from rich.style import Style
from rich.text import Text

from s7datablock.constants import S7Type, S7Value

T = TypeVar("T", bound=S7Value)


class NameType(NamedTuple):
    """Type for storing S7Field name and type information."""

    name: list[str]
    type: S7Type


class SubField(NamedTuple):
    """Represents a subfield in a structure."""

    name: str
    s7_type: S7Type
    relative_offset: int


class FormattedTableRow(NamedTuple):
    """Represents a formatted row in a table with rich text support."""

    name: str
    type: Text
    offset: str
    value: Text


class S7Field(ABC, Generic[T]):
    """Base class for all S7 PLC fields"""

    _registry: dict[str, type[S7Field]] = {}

    buffer_slice: slice
    offset: int  # Can be a byte offset or (byte, bit) tuple for bit-addressed fields
    offset_bit: int = 0  # Bit offset for bit-addressed fields
    s7_type: S7Type
    struct_fmt: str
    struct_width: int  # Width of the struct in bytes, used for packing/unpacking

    def __init_subclass__(cls, *, s7_type: S7Type | None = None, subfield_config: list[SubField] | None = None) -> None:
        super().__init_subclass__()
        if s7_type is not None:
            S7Field._registry[s7_type] = cls
            cls.s7_type = s7_type
        cls.subfield_config = subfield_config or []

    def __init__(self, offset: int, offset_bit: int = 0):
        self.offset = offset
        self.offset_bit = offset_bit
        self.struct_width = struct.calcsize(self.struct_fmt)
        self.buffer_slice = slice(offset, offset + self.struct_width)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, S7Field):
            return NotImplemented
        # Compare core attributes that define S7Field equality
        if not (self.s7_type == other.s7_type and self.offset == other.offset):
            return False
        # For boolean fields, also compare bit position
        if isinstance(self.offset, tuple) and isinstance(other.offset, tuple):
            return self.offset[1] == other.offset[1]
        return True

    def __repr__(self) -> str:
        offset_str = f"({self.offset[0]}, {self.offset[1]})" if isinstance(self.offset, tuple) else str(self.offset)
        return f"{self.__class__.__name__}(offset={offset_str}, s7_type='{self.s7_type}')"

    def unpack(self, buffer: bytearray) -> T:
        """Unpack value from buffer."""
        return cast(T, struct.unpack(self.struct_fmt, buffer[self.buffer_slice])[0])

    def pack(self, buffer: bytearray, value: T) -> None:
        """Pack value into buffer."""
        buffer[self.buffer_slice] = struct.pack(self.struct_fmt, value)

    def format_value(self, value: T) -> str:
        """Format a value for display based on its type."""
        if isinstance(value, bool):
            return str(value)
        elif isinstance(value, float):
            return f"{value:.3f}"
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)

    def get_table_row(self, name: str, buffer: bytearray, indent_level: int = 0) -> FormattedTableRow:
        """Get a formatted row for the rich text table."""
        display_name = "  " * indent_level + name
        type_style = Style(
            color={
                # Elementary types (blue family)
                "SInt": "#4169E1",  # Royal blue
                "Int": "#324AB2",  # Medium royal blue
                "DInt": "#1E4BB8",  # Deep royal blue
                # Unsigned integers (turquoise family)
                "USInt": "#20B2AA",  # Light turquoise
                "UInt": "#17887F",  # Medium turquoise
                "UDInt": "#0F5E54",  # Deep turquoise
                # Floating point (purple family)
                "Real": "#B87FD9",  # Light purple
                "LReal": "#9B4FC3",  # Deep purple
                # Word types (cyan family)
                "Byte": "#69C5CE",  # Light cyan
                "Word": "#4AACB5",  # Medium cyan
                "DWord": "#2B939C",  # Deep cyan
                # Character types (warm gray family)
                "Char": "#D4C5BC",  # Light warm gray
                "String": "#B5A69C",  # Medium warm gray
                "WChar": "#96877C",  # Deep warm gray
                # Special types with distinct colors
                "Bool": "#FFD700",  # Gold for booleans
                "DTL": "#FF8C42",  # Bright orange for date/time
                "Struct": "#F0F0F0",  # Soft white for structures
            }.get(self.s7_type, "#FFFFFF")
        )

        return FormattedTableRow(
            name=display_name,
            type=Text(self.s7_type, style=type_style),
            offset=f"{self.offset}.{self.offset_bit}",
            value=Text(self.format_value(self.unpack(buffer)), style=type_style),
        )

    @property
    def subfields(self) -> dict[str, S7Field[S7Value]]:
        """Get all the component fields of the structure."""
        assert isinstance(self.offset, int), "Offset must be an integer for subfields"
        return {
            name: S7Field.create(self.offset + rel_offset, s7_type)
            for name, s7_type, rel_offset in self.subfield_config
        }

    @staticmethod
    def create(offset: int, s7_type: str, offset_bit: int = 0) -> S7Field[S7Value]:
        """Create a new S7Field instance of the appropriate type."""
        field_class = S7Field._registry.get(s7_type)
        if field_class is None:
            raise ValueError(f"Unknown S7 type: {s7_type}")
        return field_class(offset, offset_bit)

    def __str__(self) -> str:
        return repr(self)


class S7Bool(S7Field[bool], s7_type="Bool"):
    """Boolean S7Field type."""

    struct_fmt = "?"

    def pack(self, buffer: bytearray, value: bool) -> None:
        byte = buffer[self.offset]
        if value:
            byte |= 1 << self.offset_bit
        else:
            byte &= ~(1 << self.offset_bit)
        buffer[self.offset] = byte

    def unpack(self, buffer: bytearray) -> bool:
        return bool(buffer[self.offset] & (1 << self.offset_bit))


class S7Real(S7Field[float], s7_type="Real"):
    """32-bit floating point S7Field."""

    struct_fmt = ">f"


class S7Byte(S7Field[int], s7_type="Byte"):
    """8-bit unsigned integer S7Field."""

    struct_fmt = "B"


class S7Word(S7Field[int], s7_type="Word"):
    """16-bit unsigned integer S7Field."""

    struct_fmt = ">H"


class S7DWord(S7Field[int], s7_type="DWord"):
    """32-bit unsigned integer S7Field."""

    struct_fmt = ">I"


class S7DInt(S7Field[int], s7_type="DInt"):
    """32-bit signed integer S7Field."""

    struct_fmt = ">i"


class S7UInt(S7Field[int], s7_type="UInt"):
    """16-bit unsigned integer S7Field."""

    struct_fmt = ">H"


class S7UDInt(S7Field[int], s7_type="UDInt"):
    """32-bit unsigned integer S7Field."""

    struct_fmt = ">I"


class S7USInt(S7Field[int], s7_type="USInt"):
    """8-bit unsigned integer S7Field."""

    struct_fmt = "B"


class S7Char(S7Field[str], s7_type="Char"):
    """Single character S7Field."""

    struct_fmt = "c"

    def pack(self, buffer: bytearray, value: str) -> None:
        buffer[self.buffer_slice] = value.encode("ascii")

    def unpack(self, buffer: bytearray) -> str:
        return buffer[self.buffer_slice].decode("ascii")


# Date and time types
class S7DTL(
    S7Field[datetime | None],
    s7_type="DTL",
    subfield_config=[
        SubField("YEAR", "UInt", 0),
        SubField("MONTH", "USInt", 2),
        SubField("DAY", "USInt", 3),
        SubField("WEEKDAY", "USInt", 4),
        SubField("HOUR", "USInt", 5),
        SubField("MINUTE", "USInt", 6),
        SubField("SECOND", "USInt", 7),
        SubField("NANOSECOND", "UDInt", 8),
    ],
):
    """DTL (Date and Time Long) S7Field type."""

    struct_fmt = ">HBBBBBBI"  # Year(2), Month(1), Day(1), Weekday(1), Hour(1), Minute(1), Second(1), Nanosecond(4)

    def unpack(self, buffer: bytearray) -> datetime | None:
        try:
            year, month, day, _, hour, minute, second, ns = struct.unpack(self.struct_fmt, buffer[self.buffer_slice])
            return datetime(
                year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=ns // 1000
            )
        except (ValueError, struct.error):
            return None

    def pack(self, buffer: bytearray, value: datetime | None) -> None:
        if value is None:
            buffer[self.buffer_slice] = bytes(12)
            return
        buffer[self.buffer_slice] = struct.pack(
            self.struct_fmt,
            value.year,
            value.month,
            value.day,
            value.isoweekday() % 7,  # 0=Sunday
            value.hour,
            value.minute,
            value.second,
            value.microsecond * 1000,
        )


class S7Time(S7Field[timedelta], s7_type="Time"):
    """Time duration S7Field type."""

    struct_fmt = "I"

    def unpack(self, buffer: bytearray) -> timedelta:
        ms = struct.unpack(self.struct_fmt, buffer[self.buffer_slice])[0]
        return timedelta(milliseconds=ms)

    def pack(self, buffer: bytearray, value: timedelta) -> None:
        ms = int(value.total_seconds() * 1000)
        buffer[self.buffer_slice] = struct.pack(self.struct_fmt, ms)


class S7Date(S7Field[datetime | None], s7_type="Date"):
    """Date S7Field type."""

    struct_fmt = ">H"

    def unpack(self, buffer: bytearray) -> datetime | None:
        try:
            (days,) = struct.unpack(self.struct_fmt, buffer[self.buffer_slice])
            return datetime(1990, 1, 1) + timedelta(days=days)
        except (ValueError, struct.error):
            return None

    def pack(self, buffer: bytearray, value: datetime | None) -> None:
        if value is None:
            buffer[self.buffer_slice] = bytes(2)
            return
        days = (value - datetime(1990, 1, 1)).days
        buffer[self.buffer_slice] = struct.pack(self.struct_fmt, days)


class S7TimeOfDay(S7Field[timedelta], s7_type="Time_of_Day"):
    """Time of day S7Field type."""

    struct_fmt = ">I"

    def unpack(self, buffer: bytearray) -> timedelta:
        """Unpack Time of Day value from buffer to timedelta"""
        ms_since_midnight = struct.unpack(self.struct_fmt, buffer[self.buffer_slice])[0]
        return timedelta(milliseconds=ms_since_midnight)

    def pack(self, buffer: bytearray, value: timedelta) -> None:
        """Pack a timedelta value into the buffer."""
        ms = int(value.total_seconds() * 1000)
        buffer[self.buffer_slice] = struct.pack(self.struct_fmt, ms)


class DBParseResult(NamedTuple):
    """Result type for DB parsing operations"""

    mapping: dict[str, S7Field[Any]]
    length: int


# Signed integer types
class S7Int(S7Field[int], s7_type="Int"):
    """16-bit signed integer S7Field."""

    struct_fmt = "h"
