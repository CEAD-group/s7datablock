from datetime import datetime
from io import StringIO
from time import sleep

from rich.live import Live

from s7datablock.mapping import S7DataBlock

# Example in-line definition file contents. Alternatively, you can pass a PAth to a *.db file.
df_file_contents = StringIO(
    """
        TYPE "my_udt"
        VERSION : 0.1
        STRUCT
            PLC_DQ_0 : Bool;
            PLC_DQ_1 : Bool;
            WHEN : DTL;
            Value1 : Int;
            Value2 : Real;
        END_STRUCT;
        END_TYPE
        DATA_BLOCK "my_udt"
        VERSION : 0.1
        "my_udt"
        BEGIN
        END_DATA_BLOCK
    """
)

db = S7DataBlock.from_definition_file(df_file_contents, db_number=1200)
print(db)  # This will print the structure of the data block as a table

print(repr(db))  # Print the raw representation of the data block
# In a real application, you would create a snap7 client and connect to the PLC

# client = snap7.client.Client()
# client.connect('192.168.0.1', 0, 1)

with Live(db.to_table(), refresh_per_second=10) as live:
    while True:
        # In a real application, you would call GET() here
        # db.GET(client)

        # For demo, we'll just modify some values
        db["WHEN"] = datetime.now()
        db["PLC_DQ_0"] = not db["PLC_DQ_0"]  # Toggle the boolean
        db["Value1"] = db["Value1"] + 1  # Increment the integer value
        db["Value2"] = db["Value2"] + 0.1  # Increment the real value

        # Update the display with current values
        live.update(db.to_table())
        sleep(0.2)
