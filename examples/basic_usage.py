from s7datablock.fields import S7Field
from s7datablock.mapping import BufferMapping


def main():
    """Example showing basic usage of BufferMapping with various data types"""
    buf = bytearray(10)
    var_mapping = {
        "enableFlags.enable1": S7Field.create(0, "Bool", offset_bit=0),
        "enableFlags.enable2": S7Field.create(0, "Bool", offset_bit=1),
        "enableFlags.enable3": S7Field.create(0, "Bool", offset_bit=2),
        "enableFlags.enable4": S7Field.create(0, "Bool", offset_bit=3),
        "enableFlags.enable5": S7Field.create(0, "Bool", offset_bit=4),
        "setpointHz2": S7Field.create(6, "Real"),
    }

    # Create a BufferMapping instance
    buffered_vars = BufferMapping(buf, var_mapping)

    # Set some values
    buffered_vars["enableFlags.enable4"] = True
    print("Buffer after setting enable4 (hex):", " ".join(f"{b:02X}" for b in buffered_vars.buffer))

    buffered_vars["setpointHz2"] = 23.5
    print("Buffer after setting setpointHz2 (hex):", " ".join(f"{b:02X}" for b in buffered_vars.buffer))


if __name__ == "__main__":
    main()
