import pytest

from s7datablock.fields import S7Field
from s7datablock.mapping import BufferMapping


def test_buffer_mapping_get_set_single_values():
    """Test BufferMapping with single values of different types"""
    buffer = bytearray(100)
    mapping = {
        "float": S7Field.create(offset=0, s7_type="Real"),
        "int": S7Field.create(offset=4, s7_type="Int"),
        "bool": S7Field.create(offset=8, offset_bit=0, s7_type="Bool"),
    }
    bm = BufferMapping(buffer, mapping)

    # Test float value
    bm["float"] = 1.23
    assert isinstance(bm["float"], float)
    assert abs(bm["float"] - 1.23) < 0.0001

    # Test int value
    bm["int"] = 42
    assert isinstance(bm["int"], int)
    assert bm["int"] == 42

    # Test bool value
    bm["bool"] = True
    assert isinstance(bm["bool"], bool)
    assert bm["bool"] is True
    bm["bool"] = False
    assert bm["bool"] is False


def test_buffer_mapping_errors():
    """Test error conditions in BufferMapping"""
    buffer = bytearray(100)
    mapping = {
        "float": S7Field.create(offset=0, s7_type="Real"),
    }
    bm = BufferMapping(buffer, mapping)

    # Test accessing non-existent key
    with pytest.raises(KeyError):
        _ = bm["non_existent"]

    # Test setting non-existent key
    with pytest.raises(KeyError):
        bm["non_existent"] = 42.0


def test_buffer_mapping_str():
    """Test the string representation of BufferMapping"""
    buffer = bytearray(100)
    mapping = {
        "float": S7Field.create(offset=0, s7_type="Real"),
        "int": S7Field.create(offset=4, s7_type="Int"),
        "bool": S7Field.create(offset=8, s7_type="Bool", offset_bit=0),
        "byte": S7Field.create(offset=10, s7_type="Byte"),
        "word": S7Field.create(offset=12, s7_type="Word"),
        "dword": S7Field.create(offset=14, s7_type="DWord"),
        "char": S7Field.create(offset=18, s7_type="Char"),
        "time": S7Field.create(offset=20, s7_type="Time"),
        "date": S7Field.create(offset=24, s7_type="Date"),
        "tod": S7Field.create(offset=26, s7_type="Time_of_Day"),
    }
    bm = BufferMapping(buffer, mapping)

    # Set some values to test string formatting
    bm["float"] = 1.23
    bm["int"] = 42
    bm["bool"] = True
    bm["byte"] = 255  # type: ignore
    bm["word"] = 65535  # type: ignore
    bm["dword"] = 4294967295  # type: ignore

    # Test __repr__
    repr_str = repr(bm)
    assert "float" in repr_str
    assert "int" in repr_str
    assert "bool" in repr_str

    # Test __str__
    str_output = str(bm)
    assert isinstance(str_output, str)
    assert "Data Block Structure" in str_output

    # Test various data type strings are present
    assert "Real" in str_output
    assert "Int" in str_output
    assert "Bool" in str_output
    assert "Byte" in str_output
    assert "Word" in str_output
    assert "DWord" in str_output
    assert "Char" in str_output
    assert "Time" in str_output
    assert "Date" in str_output
    assert "Time_of_Day" in str_output

    # Test value formatting
    assert "1.230" in str_output  # float with 3 decimals
    assert "42" in str_output  # int
    assert "True" in str_output  # bool
    assert "255" in str_output  # byte
    assert "65535" in str_output  # word
    assert "4294967295" in str_output  # dword
