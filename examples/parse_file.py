from datetime import datetime
from io import StringIO

from s7datablock.mapping import S7DataBlock

db_buff = StringIO(
    """
TYPE "my_udt"
VERSION : 0.1
   STRUCT
      PLC_DQ_0 : Bool;
      WHEN : DTL;
      a_word : Word;
      a_dword : DWord;
   END_STRUCT;
END_TYPE
DATA_BLOCK "my_udt"
VERSION : 0.1
"my_udt"
BEGIN
END_DATA_BLOCK
"""
)

db = S7DataBlock.from_definition_file(db_buff, db_number=1200, nesting_depth_to_skip=0)

# Set initial datetime value
now = datetime(2025, 7, 9, 14, 30, 45, 123456)  # microseconds = 123456
db["my_udt.WHEN"] = now
print("Initial datetime:", db["my_udt.WHEN"])

# Demonstrate DTL subfield access
print("\nAccessing and modifying DTL subfields:")
print("Current month:", db["my_udt.WHEN.MONTH"])
db["my_udt.WHEN.MONTH"] = 12  # Change month to December
print("After changing month:", db["my_udt.WHEN"])


# Display the full structure with values
print("\nFull structure:")
print(db)
