"""Test DTL structure parsing from a DB definition."""
from datetime import datetime
from io import StringIO

import pytest

from s7datablock.mapping import S7DataBlock


@pytest.fixture
def sample_dtl_db():
    """Create a sample DB with a DTL S7Field."""
    db_buff = StringIO(
        """
TYPE "my_udt"
VERSION : 0.1
   STRUCT
      PLC_DQ_0 : Bool;
      WHEN : DTL;
   END_STRUCT;
END_TYPE
DATA_BLOCK "my_udt"
VERSION : 0.1
"my_udt"
BEGIN
END_DATA_BLOCK
"""
    )
    return S7DataBlock.from_definition_file(db_buff, db_number=1200, nesting_depth_to_skip=0)


def test_db_structure(sample_dtl_db):
    """Test that the DB structure is correctly parsed."""
    assert "my_udt.PLC_DQ_0" in sample_dtl_db
    assert "my_udt.WHEN" in sample_dtl_db


def test_dtl_field_operations(sample_dtl_db):
    """Test operations on a DTL S7Field using the buffer-passing pattern."""
    assert sample_dtl_db["my_udt.WHEN"] is None
    assert sample_dtl_db["my_udt.WHEN.YEAR"] == 0
    year, month, day, hour, minute, second, microsecond = (2025, 7, 9, 14, 30, 45, 123456)
    timestamp = datetime(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond
    )
    sample_dtl_db["my_udt.WHEN"] = timestamp
    assert sample_dtl_db["my_udt.WHEN.YEAR"] == year
    assert sample_dtl_db["my_udt.WHEN.MONTH"] == month
    assert sample_dtl_db["my_udt.WHEN.DAY"] == day
    assert sample_dtl_db["my_udt.WHEN.WEEKDAY"] == timestamp.weekday() + 1  # S7 weekday starts at 1
    assert sample_dtl_db["my_udt.WHEN.HOUR"] == hour
    assert sample_dtl_db["my_udt.WHEN.MINUTE"] == minute
    assert sample_dtl_db["my_udt.WHEN.SECOND"] == second
    assert sample_dtl_db["my_udt.WHEN.NANOSECOND"] == microsecond * 1000
    assert sample_dtl_db["my_udt.WHEN"] == timestamp

    sample_dtl_db["my_udt.WHEN.YEAR"] = 2026
    assert sample_dtl_db["my_udt.WHEN"].year == 2026
