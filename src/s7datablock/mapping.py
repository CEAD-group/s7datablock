from collections.abc import ItemsView, MutableMapping, ValuesView
from datetime import datetime

import snap7
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text

from s7datablock.fields import S7Field, S7Value
from s7datablock.parser import parse_db_file

ElementalType = float | int | bool | datetime


class BufferMapping(MutableMapping[str, ElementalType]):
    """A mapping that allows for easy access to a buffer of bytes.

    The buffer is Siemens S7 compatible (for unoptimised DB's), including the bit packing
    where multiple bools are packed into a single byte.

    Args:
        buffer: A bytearray containing the raw data.
        mapping: A dict mapping names to either:
            - Field or S7Field objects (recommended)

    """

    def __init__(self, buffer: bytearray, mapping: dict[str, S7Field[S7Value]]) -> None:
        self.buffer = buffer
        self.mapping = mapping

    def __getitem__(self, name: str):
        # Check if this is a DTL subfield access (e.g. "datetime.SECOND")
        if name in self.mapping:
            field: S7Field = self.mapping[name]
            return field.unpack(self.buffer)
        raise KeyError(f"'{name}' not found")

    def __setitem__(self, name: str, value) -> None:
        if name in self.mapping:
            field: S7Field = self.mapping[name]
            return field.pack(self.buffer, value)
        raise KeyError(f"'{name}' not found")

    def __delitem__(self, name: str) -> None:
        """Delete an item from the mapping.

        Not supported as the buffer has a fixed size and structure.
        """
        raise NotImplementedError("Cannot delete items from a fixed buffer mapping")

    def __len__(self) -> int:
        """Return the number of fields in the mapping."""
        return len(self.mapping)

    def __iter__(self):
        """Return an iterator over the field names."""
        return iter(self.mapping)

    def __repr__(self) -> str:
        # return the unpacked values instead of the mapping S7Field
        return {k: self[k] for k in self.mapping.keys()}.__repr__()

    def __str__(self) -> str:
        """Generate a rich table representation of the data block structure.

        Returns a formatted string showing field names, data types, offsets, and current values
        with proper hierarchical indentation.
        """
        total_size = self.total_size()
        table = self.to_table()

        console = Console(record=True, width=120)
        with console.capture() as capture:
            console.print()  # Empty line before table
            for _ in range(17):
                console.print(" ", end="")
            console.print(table)
            console.print(f"             Total size: {total_size} bytes")
            console.print()  # Empty line after

        return capture.get()

    def to_table(self) -> Table:
        table = Table(
            show_edge=True,
            show_header=True,
            show_lines=False,
            padding=(0, 1),
            title="\nData Block Structure",
            width=None,
        )

        table.add_column("Name", justify="left", min_width=16, style=Style(color="bright_cyan", bold=True))
        table.add_column("Data type", justify="left", min_width=11)
        table.add_column("Offset", justify="right", min_width=8)
        table.add_column("Value", justify="left", min_width=11)

        prev_bases = []
        prev_sub = ""
        for name, field in self.mapping.items():
            (*bases, sub) = name.split(".")  # Split on the last dot to get the parent name
            indent_level = len(name.split(".")) - 1
            if bases != prev_bases:
                # Add an empty row for the new base
                n = 0
                while n < len(bases) and n < len(prev_bases):
                    if bases[n] != prev_bases[n]:
                        break
                    n += 1
                if bases and bases[-1] == prev_sub:
                    # If the last base is the same as the previous sub, we don't need to add a new row
                    n += 1

                for m in range(n, len(bases)):
                    # Add a new base row
                    table.add_row(
                        "  " * m + bases[m],  # Indent based on the hierarchy level
                        Text("Struct", Style(color="bright_white", bold=True)),
                        "",
                        "",
                    )
                prev_bases = bases

            # Add a row to the table
            table.add_row(*field.get_table_row(name=name, indent_level=indent_level, buffer=self.buffer))
            prev_sub = sub

        return table

    def total_size(self) -> int:
        """Calculate the total size of the buffer based on the maximum offset of all fields."""
        total_size = max(field.offset + field.struct_width for field in self.mapping.values())
        return total_size

    def keys(self):
        """Returns a view of the field names in the mapping."""
        return self.mapping.keys()

    def values(self):
        """Returns a view of the current values in the mapping."""
        return ValuesView(self)

    def items(self):
        """Returns a view of (name, value) pairs for all fields in the mapping."""
        return ItemsView(self)

    def to_dict(self) -> dict[str, ElementalType]:
        """Convert the mapping to a regular dictionary.

        Returns:
            A dictionary containing all field names and their current values
        """
        return dict(self.items())


class S7DataBlock(BufferMapping):
    buffer: bytearray
    db_number: int | None
    db_size: int

    def __init__(
        self,
        buffer: bytearray,
        mapping: dict[str, S7Field],
        db_number: int | None,
        db_size: int,
    ):
        super().__init__(buffer, mapping)
        self.db_number = db_number
        self.db_size = db_size

    @classmethod
    def from_definition_file(cls, path, db_number: int | None = None, nesting_depth_to_skip: int = 1) -> "S7DataBlock":
        """Create an S7DataBlock from a TIA Portal export file.

        Args:
            path: Path to the TIA Portal export file
            db_number: Optional DB number for PLC communication

        Returns:
            S7DataBlock: The created datablock
        """
        mapping, size = parse_db_file(path, nesting_depth_to_skip=nesting_depth_to_skip)
        return cls(buffer=bytearray(size), mapping=mapping, db_number=db_number, db_size=size)

    def GET(self, client: snap7.client.Client):
        """Read all values from PLC.

        Args:
            client: snap7.client.Client instance
        """
        if self.db_number is None:
            raise ValueError("No DB number specified")

        self.buffer = client.db_read(self.db_number, 0, self.db_size)

    def SET(self, client: snap7.client.Client):
        """Write all values to PLC.

        Args:
            client: snap7.client.Client instance
        """
        if self.db_number is None:
            raise ValueError("No DB number specified")

        client.db_write(self.db_number, 0, self.buffer)

    # Alias methods for backward compatibility
    pull = GET
    push = SET
