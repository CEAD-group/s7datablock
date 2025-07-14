from pathlib import Path

import pytest

from s7datablock.mapping import S7DataBlock


@pytest.fixture
def s7_data_block():
    return S7DataBlock.from_definition_file(Path("tests/definitions/s7_1200_out.db"), db_number=1200)


def test_s7_data_block_buffer(s7_data_block):
    assert s7_data_block.buffer == bytearray(16)


def test_s7_data_block_key(s7_data_block):
    assert s7_data_block["PLC_DQ_1"] is False


def test_s7_data_block_key_error(s7_data_block):
    with pytest.raises(KeyError):
        s7_data_block["unknown_key"]


def test_s7_data_block_key_assignment(s7_data_block):
    s7_data_block["PLC_DQ_1"] = True
    assert s7_data_block["PLC_DQ_1"] is True


def test_s7_data_block_buffer_after_assignment(s7_data_block):
    s7_data_block["PLC_DQ_1"] = True
    assert s7_data_block.buffer == bytearray(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")


# @pytest.mark.parametrize(
#     "fields, expected_size",
#     [
#         ([S7Field.create(name_or_names=["a"], type="Bool", format="H")], 2),
#         ([S7Field.create(name_or_names=["a", "b"], type="Bool", format="H")], 2),
#         (
#             [
#                 S7Field.create(name_or_names=["a"], type="Bool", format="H"),
#                 S7Field.create(name_or_names=["b"], type="Bool", format="H"),
#             ],
#             4,
#         ),
#     ],
#     ids=["single_field_a", "merged_fields_a_b", "separate_fields_a_and_b"],
# )
# def test_size_calculation(fields, expected_size):
#     assert S7DataBlock.from_fields(fields, db_number=0).db_size == expected_size
