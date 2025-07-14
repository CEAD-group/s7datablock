import pytest

from s7datablock.mapping import BufferMapping, S7Field


# Creating a fixture for buffer and mapping that can be reused across tests
@pytest.fixture(scope="function")
def mapping():
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


def test_default_values(mapping):
    assert mapping["enable1"] is False
    assert mapping["setpoint"] == 0


def test_unknown_key(mapping):
    with pytest.raises(KeyError):
        mapping["unknown_key"]


def test_set_and_get_float(mapping):
    mapping["setpoint"] = 23.5
    assert mapping["setpoint"] == 23.5


def test_set_and_get_boolean(mapping):
    mapping["enable2"] = True
    assert mapping["enable1"] is False
    assert mapping["enable2"] is True
    assert mapping["enable3"] is False

    mapping["enable2"] = False
    assert mapping["enable2"] is False
