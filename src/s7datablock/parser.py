"""Functions to parse DB definitions exported from TIA Portal."""
import math
from collections.abc import Iterator
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Any

from s7datablock.fields import DBParseResult, NameType, S7Field
from s7datablock.grammar import program


def resolve_data_types(types: dict[str, Any], prefix: list[str], d: Any) -> Iterator[tuple[list[str], Any]]:
    if isinstance(d, dict):
        for k, v in d.items():
            yield from resolve_data_types(types, prefix + [k], v)
    elif d in types:
        yield from resolve_data_types(types, prefix, deepcopy(types[d]))
    else:
        yield prefix, d


def parse_db_file(p: Path | StringIO, nesting_depth_to_skip=1) -> DBParseResult:
    """Parse a DB file and return a S7Field mapping and total size.

    Args:
        p (Path): Path to the DB file
        nesting_depth_to_skip (int, optional): How many levels in the nested data to skip when generating the fieldnames for nested fields.

    Returns:
        tuple[dict[str, S7Field], int]: The S7Field mapping and total size in bytes
    """
    if isinstance(p, Path):
        string = p.read_text(encoding="utf-8-sig")
    elif isinstance(p, StringIO):
        string = p.read()
    else:
        raise TypeError("Input must be a Path or StringIO")

    if nesting_depth_to_skip < 0:
        raise ValueError("nesting_depth_to_skip must be a non-negative integer")
    result = program.parseString(string, parse_all=True).as_dict()
    types = result["TYPES"]
    data = result["DATA_BLOCK"]
    result["BEGIN"]  # default values could be handled here

    # Get the flattened list of fields and types
    name_types = [NameType(name=k, type=v) for k, v in list(resolve_data_types(types, [], data))]

    # Process fields into S7Field mapping
    mapping = {}
    offset = 0
    current_bools: list[str] = []
    prev_base_name = ""
    for i in name_types:
        name_parts = i.name[nesting_depth_to_skip:]
        full_name = ".".join(name_parts)
        base_name = ".".join(name_parts[:-1])
        if current_bools and (base_name != prev_base_name or i.type != "Bool"):
            offset += flush_bools(current_bools, offset, mapping)
            current_bools = []
        prev_base_name = base_name
        if i.type == "Bool":
            current_bools.append(full_name)
            continue

        field = S7Field.create(offset, i.type)
        mapping[full_name] = field
        for k, v in field.subfields.items():
            mapping[f"{full_name}.{k}"] = v
        offset += field.struct_width

    if current_bools:
        offset += flush_bools(current_bools, offset, mapping)

    return DBParseResult(mapping=mapping, length=offset)


def flush_bools(current_bools: list[str], offset: int, mapping: dict[str, S7Field]) -> int:
    """Pack boolean fields into byte-aligned memory and update the mapping."""
    for i, name in enumerate(current_bools):
        mapping[name] = S7Field.create(offset + (i // 8), "Bool", offset_bit=i % 8)
    return 2 * math.ceil(len(current_bools) / 16)
