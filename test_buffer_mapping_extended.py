import struct
from datetime import time

from new_api import FieldLTOD


def test_ltod():
    """Test LTOD (LTIME_OF_DAY) S7Field type"""
    S7Field = FieldLTOD(0)
    buffer = bytearray(8)

    # Test midnight (00:00:00.000000000)
    midnight = time(0, 0, 0)
    S7Field.pack(buffer, midnight)
    assert S7Field.unpack(buffer) == midnight
    assert struct.unpack(">Q", buffer)[0] == 0

    # Test noon (12:00:00.000000000)
    noon = time(12, 0, 0)
    S7Field.pack(buffer, noon)
    assert S7Field.unpack(buffer) == noon
    assert struct.unpack(">Q", buffer)[0] == 12 * 3600 * 1_000_000_000

    # Test 23:59:59.999999
    max_time = time(23, 59, 59, 999999)
    S7Field.pack(buffer, max_time)
    assert S7Field.unpack(buffer) == max_time
    # We don't check exact nanoseconds due to microsecond rounding in time objects

    # Test with microsecond precision
    t = time(12, 34, 56, 789123)
    S7Field.pack(buffer, t)
    assert S7Field.unpack(buffer) == t
