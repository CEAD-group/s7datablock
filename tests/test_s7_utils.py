from datetime import datetime

import pytest

from s7datablock.fields import S7Field
from s7datablock.mapping import BufferMapping


# Common test fixtures
@pytest.fixture(scope="function")
def basic_buffer() -> BufferMapping:
    """Basic buffer with boolean and float values"""
    buf = bytearray(10)
    var_mapping = {
        "enable1": S7Field.create(0, "Bool", offset_bit=0),
        "enable2": S7Field.create(0, "Bool", offset_bit=1),
        "enable3": S7Field.create(0, "Bool", offset_bit=2),
        "enable4": S7Field.create(0, "Bool", offset_bit=3),
        "enable5": S7Field.create(0, "Bool", offset_bit=4),
        "setpoint": S7Field.create(2, "Real"),
    }
    return BufferMapping(buf, var_mapping)


@pytest.fixture(scope="function")
def all_types_buffer():
    """Buffer with all supported S7 data types"""
    buffer = bytearray(100)
    mapping = {
        "float": S7Field.create(offset=0, s7_type="Real"),
        "int": S7Field.create(offset=4, s7_type="Int"),
        "bool": S7Field.create(offset=8, s7_type="Bool"),
        "byte": S7Field.create(offset=10, s7_type="Byte"),
        "word": S7Field.create(offset=11, s7_type="Word"),
        "dword": S7Field.create(offset=13, s7_type="DWord"),
        "char": S7Field.create(offset=17, s7_type="Char"),
    }
    return BufferMapping(buffer, mapping)


@pytest.fixture(scope="function")
def dtl_buffer():
    """Buffer with DTL (Date and Time Long) data type"""
    buf = bytearray(16)
    var_mapping = {
        "flags.enable0": S7Field.create(0, "Bool", offset_bit=0),
        "flags.enable1": S7Field.create(0, "Bool", offset_bit=1),
        "flags.enable2": S7Field.create(0, "Bool", offset_bit=2),
        "datetime": S7Field.create(2, "DTL"),
        "datetime.YEAR": S7Field.create(2, "UInt"),
        "datetime.MONTH": S7Field.create(4, "USInt"),
        "datetime.DAY": S7Field.create(5, "USInt"),
        "datetime.WEEKDAY": S7Field.create(6, "USInt"),
        "datetime.HOUR": S7Field.create(7, "USInt"),
        "datetime.MINUTE": S7Field.create(8, "USInt"),
        "datetime.SECOND": S7Field.create(9, "USInt"),
        "datetime.NANOSECOND": S7Field.create(10, "UDInt"),
        "a_word": S7Field.create(14, "DWord"),
    }

    return BufferMapping(buf, var_mapping)


# Basic functionality tests
class TestBasicFunctionality:
    """Tests for basic BufferMapping functionality"""

    def test_default_values(self, basic_buffer):
        """Test default values after initialization"""
        assert basic_buffer["enable1"] is False
        assert basic_buffer["setpoint"] == 0

    def test_get_set_boolean(self, basic_buffer):
        """Test setting and getting boolean values"""
        basic_buffer["enable2"] = True
        assert basic_buffer["enable1"] is False
        assert basic_buffer["enable2"] is True
        assert basic_buffer["enable3"] is False

        basic_buffer["enable2"] = False
        assert basic_buffer["enable2"] is False

    def test_get_set_float(self, basic_buffer):
        """Test setting and getting float values"""
        basic_buffer["setpoint"] = 23.5
        assert basic_buffer["setpoint"] == 23.5


# Error handling and validation tests
class TestErrorHandling:
    """Tests for error conditions and input validation"""

    def test_unknown_key(self, basic_buffer):
        """Test accessing non-existent key"""
        with pytest.raises(KeyError):
            basic_buffer["unknown_key"]


# String representation tests
class TestStringRepresentation:
    """Tests for string formatting and representation"""

    def test_str_format(self, basic_buffer):
        """Test the __str__ output format"""
        print(basic_buffer)
        expected_output = """
                            Data Block Structure
            ┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
            ┃ Name             ┃ Data type   ┃   Offset ┃ Value       ┃
            ┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
            │ enable1          │ Bool        │      0.0 │ False       │
            │ enable2          │ Bool        │      0.1 │ False       │
            │ enable3          │ Bool        │      0.2 │ False       │
            │ enable4          │ Bool        │      0.3 │ False       │
            │ enable5          │ Bool        │      0.4 │ False       │
            │ setpoint         │ Real        │      2.0 │ 0.000       │
            └──────────────────┴─────────────┴──────────┴─────────────┘
                        Total size: 6 bytes
            """

        assert [ln.strip() for ln in (str(basic_buffer)).splitlines() if ln.strip()] == [
            ln.strip() for ln in expected_output.splitlines() if ln.strip()
        ]


# Tests for DTL functionality
class TestDTLFunctionality:
    """Tests for DTL (Date and Time Long) data type"""

    def test_dtl_basic_operations(self, dtl_buffer):
        """Test basic operations with DTL S7Field"""
        # Initial state of bool S7Field
        dtl_buffer["flags.enable1"] = True
        assert dtl_buffer["flags.enable1"] is True

        # Set datetime through datetime object
        timestamp = datetime(2025, 2, 9, 10, 2, 5, 123)
        dtl_buffer["datetime"] = timestamp
        assert dtl_buffer["datetime"] == timestamp

        # Read individual fields
        assert dtl_buffer["datetime.YEAR"] == 2025
        assert dtl_buffer["datetime.MONTH"] == 2
        assert dtl_buffer["datetime.DAY"] == 9
        assert dtl_buffer["datetime.HOUR"] == 10
        assert dtl_buffer["datetime.MINUTE"] == 2
        assert dtl_buffer["datetime.SECOND"] == 5
        assert dtl_buffer["datetime.NANOSECOND"] == 123000  # microseconds * 1000

    def test_dtl_subfield_modification(self, dtl_buffer):
        """Test modifying DTL subfields"""
        # Set initial date
        now = datetime(2025, 2, 9, 10, 2, 5, 123)
        dtl_buffer["datetime"] = now

        # Modify month S7Field
        dtl_buffer["datetime.MONTH"] = 7
        assert dtl_buffer["datetime.MONTH"] == 7

        # The datetime object should reflect the change
        assert dtl_buffer["datetime"].month == 7
        assert dtl_buffer["datetime"].year == 2025  # Other fields unchanged
