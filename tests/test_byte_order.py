"""S7 stores every multi-byte value big-endian. These tests decode KNOWN raw bytes,
so a field format without an explicit ">" fails here instead of round-tripping
cleanly through pack() and unpack() with the same wrong byte order."""

from datetime import timedelta

import pytest

from s7datablock.fields import S7Field

BIG_ENDIAN_CASES = [
    ("Int", bytes([0x02, 0xD0]), 720),
    ("Int", bytes([0xFF, 0xFE]), -2),
    ("UInt", bytes([0x02, 0xD0]), 720),
    ("Word", bytes([0x02, 0xD0]), 720),
    ("DInt", bytes([0x00, 0x01, 0x00, 0x02]), 65538),
    ("DInt", bytes([0xFF, 0xFF, 0xFF, 0xFE]), -2),
    ("UDInt", bytes([0x00, 0x01, 0x00, 0x02]), 65538),
    ("DWord", bytes([0x00, 0x01, 0x00, 0x02]), 65538),
    ("Real", bytes([0x43, 0x65, 0x00, 0x00]), 229.0),
    ("Time", bytes([0x00, 0x00, 0x03, 0xE8]), timedelta(seconds=1)),
    ("Time", bytes([0xFF, 0xFF, 0xFC, 0x18]), timedelta(seconds=-1)),
    ("Time_of_Day", bytes([0x00, 0x00, 0x03, 0xE8]), timedelta(seconds=1)),
]


@pytest.mark.parametrize("s7_type,raw,expected", BIG_ENDIAN_CASES)
def test_unpack_reads_big_endian(s7_type, raw, expected):
    field = S7Field.create(offset=2, s7_type=s7_type)
    buffer = bytearray(2) + bytearray(raw) + bytearray(2)
    assert field.unpack(buffer) == expected


@pytest.mark.parametrize("s7_type,raw,expected", BIG_ENDIAN_CASES)
def test_pack_writes_big_endian(s7_type, raw, expected):
    field = S7Field.create(offset=2, s7_type=s7_type)
    buffer = bytearray(len(raw) + 4)
    field.pack(buffer, expected)
    assert bytes(buffer[2 : 2 + len(raw)]) == raw
