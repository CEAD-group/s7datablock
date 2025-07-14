from io import StringIO
from pathlib import Path

import pytest

from s7datablock.fields import DBParseResult, S7Field
from s7datablock.parser import parse_db_file


@pytest.fixture
def sample_db_file(tmp_path) -> Path:
    """Create a temporary DB file for testing."""
    db_path = tmp_path / "test.db"
    db_path.write_text(SAMPLE_DB)
    return db_path


# Test data that will be used across multiple tests
SAMPLE_DB = """
TYPE "s7_1200_out_udt"
VERSION : 0.1
   STRUCT
      PLC_DQ_0 : Bool;
      PLC_DQ_1 : Bool;
      PLC_DQ_2 : Bool;
      PLC_DQ_3 : Bool;
      PLC_DQ_4 : Bool;
      SB_AQ_0 : Int;
      TIMEFIELD : DTL;
   END_STRUCT;
END_TYPE

DATA_BLOCK "s7_1200_output"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
"s7_1200_out_udt"
BEGIN
END_DATA_BLOCK
"""
SAMPLE_DB_MANY_BOOLS = """
TYPE "s7_1200_out_udt"
VERSION : 0.1
   STRUCT
      B1 : Bool;
      B2 : Bool;
      B3 : Bool;
      B4 : Bool;
      B5 : Bool;
      B6 : Bool;
      B7 : Bool;
      B8 : Bool;
      B9 : Bool;
      B10 : Bool;
      B11 : Bool;
      B12 : Bool;
      B13 : Bool;
      B14 : Bool;
      B15 : Bool;
      B16 : Bool;
      B17 : Bool;
      B18 : Bool;
      R1 : Real;
   END_STRUCT;
END_TYPE

DATA_BLOCK "s7_1200_output"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
"s7_1200_out_udt"
BEGIN
END_DATA_BLOCK
"""
SAMPLE_DB_16_BOOLS = """
TYPE "s7_1200_out_udt"
VERSION : 0.1
   STRUCT
      B1 : Bool;
      B2 : Bool;
      B3 : Bool;
      B4 : Bool;
      B5 : Bool;
      B6 : Bool;
      B7 : Bool;
      B8 : Bool;
      B9 : Bool;
      B10 : Bool;
      B11 : Bool;
      B12 : Bool;
      B13 : Bool;
      B14 : Bool;
      B15 : Bool;
      B16 : Bool;
      R1 : Real;
   END_STRUCT;
END_TYPE

DATA_BLOCK "s7_1200_output"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
"s7_1200_out_udt"
BEGIN
END_DATA_BLOCK
"""


# Smoketest: try the parsing function on all *.db files in configs
@pytest.mark.parametrize(
    "filepath",
    Path("tests/definitions").glob("**/*.db"),
    ids=str,
)
def test_parse_db_definitions(filepath: Path):
    """Verify that all DB files in the test directory can be parsed."""
    result = parse_db_file(filepath)
    assert isinstance(result, DBParseResult)
    assert result.length > 0
    assert len(result.mapping) > 0


def test_parse_db_from_stringio():
    """Test parsing DB definition from a StringIO object."""
    string_io = StringIO(SAMPLE_DB)
    result = parse_db_file(string_io)
    assert isinstance(result, DBParseResult)
    assert result.length == 16
    assert "PLC_DQ_0" in result.mapping


def test_parse_db_no_nesting_depth_to_skip():
    """Test parsing with nesting_depth_to_skip=0 to keep full S7Field names."""
    result = parse_db_file(Path("tests/definitions/s7_1200_out.db"), nesting_depth_to_skip=0)

    assert isinstance(result, DBParseResult)
    assert result.length == 16
    assert result.mapping == {
        "s7_1200_output.PLC_DQ_0": S7Field.create(offset=0, s7_type="Bool", offset_bit=0),
        "s7_1200_output.PLC_DQ_1": S7Field.create(offset=0, s7_type="Bool", offset_bit=1),
        "s7_1200_output.PLC_DQ_2": S7Field.create(offset=0, s7_type="Bool", offset_bit=2),
        "s7_1200_output.PLC_DQ_3": S7Field.create(offset=0, s7_type="Bool", offset_bit=3),
        "s7_1200_output.PLC_DQ_4": S7Field.create(offset=0, s7_type="Bool", offset_bit=4),
        "s7_1200_output.SB_AQ_0": S7Field.create(offset=2, s7_type="Int"),
        "s7_1200_output.TIMEFIELD": S7Field.create(offset=4, s7_type="DTL"),
        "s7_1200_output.TIMEFIELD.YEAR": S7Field.create(offset=4, s7_type="UInt"),
        "s7_1200_output.TIMEFIELD.MONTH": S7Field.create(s7_type="USInt", offset=6),
        "s7_1200_output.TIMEFIELD.DAY": S7Field.create(s7_type="USInt", offset=7),
        "s7_1200_output.TIMEFIELD.WEEKDAY": S7Field.create(offset=8, s7_type="USInt"),
        "s7_1200_output.TIMEFIELD.HOUR": S7Field.create(s7_type="USInt", offset=9),
        "s7_1200_output.TIMEFIELD.MINUTE": S7Field.create(s7_type="USInt", offset=10),
        "s7_1200_output.TIMEFIELD.SECOND": S7Field.create(offset=11, s7_type="USInt"),
        "s7_1200_output.TIMEFIELD.NANOSECOND": S7Field.create(offset=12, s7_type="UDInt"),
    }


def test_parse_db_with_nesting_depth_to_skip():
    """Test parsing with nesting_depth_to_skip=1 to skip top-level UDT name."""
    result = parse_db_file(Path("tests/definitions/s7_1200_out.db"), nesting_depth_to_skip=1)

    assert isinstance(result, DBParseResult)
    assert result.length == 16
    assert result.mapping == {
        "PLC_DQ_0": S7Field.create(offset=0, s7_type="Bool", offset_bit=0),
        "PLC_DQ_1": S7Field.create(offset=0, s7_type="Bool", offset_bit=1),
        "PLC_DQ_2": S7Field.create(offset=0, s7_type="Bool", offset_bit=2),
        "PLC_DQ_3": S7Field.create(offset=0, s7_type="Bool", offset_bit=3),
        "PLC_DQ_4": S7Field.create(offset=0, s7_type="Bool", offset_bit=4),
        "SB_AQ_0": S7Field.create(offset=2, s7_type="Int"),
        "TIMEFIELD": S7Field.create(offset=4, s7_type="DTL"),
        "TIMEFIELD.YEAR": S7Field.create(offset=4, s7_type="UInt"),
        "TIMEFIELD.MONTH": S7Field.create(s7_type="USInt", offset=6),
        "TIMEFIELD.DAY": S7Field.create(s7_type="USInt", offset=7),
        "TIMEFIELD.WEEKDAY": S7Field.create(offset=8, s7_type="USInt"),
        "TIMEFIELD.HOUR": S7Field.create(s7_type="USInt", offset=9),
        "TIMEFIELD.MINUTE": S7Field.create(s7_type="USInt", offset=10),
        "TIMEFIELD.SECOND": S7Field.create(offset=11, s7_type="USInt"),
        "TIMEFIELD.NANOSECOND": S7Field.create(offset=12, s7_type="UDInt"),
    }


def test_parse_db_invalid_input(sample_db_file):
    """Test that invalid inputs raise appropriate exceptions."""
    # Test invalid nesting depth
    with pytest.raises(ValueError, match="nesting_depth_to_skip must be a non-negative integer"):
        parse_db_file(sample_db_file, nesting_depth_to_skip=-1)

    # Test invalid input type
    with pytest.raises(TypeError, match="Input must be a Path or StringIO"):
        parse_db_file(123)  # type: ignore

    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        parse_db_file(Path("non_existent_file.db"))


def test_parse_db_many_bools():
    """Test parsing a DB file with many boolean fields."""
    string_io = StringIO(SAMPLE_DB_MANY_BOOLS)
    result = parse_db_file(string_io)

    assert isinstance(result, DBParseResult)
    assert result.length == 8
    assert len(result.mapping) == 19

    # Check that all boolean fields are correctly mapped
    assert result.mapping["B1"].offset == 0
    assert result.mapping["B1"].offset_bit == 0
    assert result.mapping["B16"].offset == 1
    assert result.mapping["B16"].offset_bit == 7
    assert result.mapping["B17"].offset == 2
    assert result.mapping["B17"].offset_bit == 0
    assert result.mapping["B18"].offset == 2
    assert result.mapping["B18"].offset_bit == 1
    assert result.mapping["R1"].offset == 4


def test_parse_db_16_bools():
    """Test parsing a DB file with many boolean fields."""
    string_io = StringIO(SAMPLE_DB_16_BOOLS)
    result = parse_db_file(string_io)

    assert isinstance(result, DBParseResult)
    assert result.length == 6
    assert len(result.mapping) == 17

    # Check that all boolean fields are correctly mapped
    assert result.mapping["B1"].offset == 0
    assert result.mapping["B1"].offset_bit == 0
    assert result.mapping["B16"].offset == 1
    assert result.mapping["B16"].offset_bit == 7
    assert result.mapping["R1"].offset == 2
