import numpy as np
import sys
import os

def main():
    if len(sys.argv) != 7:
        print("Usage: python swap_endian.py X Y Z dtype endianness filename")
        print("Example: python swap_endian.py 128 128 64 float32 little data.bin")
        sys.exit(1)

    X = int(sys.argv[1])
    Y = int(sys.argv[2])
    Z = int(sys.argv[3])
    dtype = sys.argv[4].lower()
    endianness = sys.argv[5].lower()
    filename = sys.argv[6]

    if endianness not in ['little', 'big']:
        print("Endianness must be 'little' or 'big'")
        sys.exit(1)

    # Map dtype string to numpy code
    dtype_map = {
        'float32': 'f4',
        'float64': 'f8',
        'int16': 'i2',
        'int32': 'i4',
        'int64': 'i8',
        'uint8': 'u1',
        'uint16': 'u2',
        'uint32': 'u4',
        'uint64': 'u8',
    }
    if dtype not in dtype_map:
        print(f"Unsupported dtype: {dtype}")
        sys.exit(1)

    endian_char = '<' if endianness == 'little' else '>'
    dtype_np = np.dtype(endian_char + dtype_map[dtype])

    # Read the data
    with open(filename, 'rb') as f:
        data = np.fromfile(f, dtype=dtype_np)

    expected_size = X * Y * Z
    if data.size != expected_size:
        print(f"Data size mismatch! Expected {expected_size} elements, got {data.size}.")
        sys.exit(1)

    data = data.reshape((Z, Y, X))

    # Swap endianness
    data_swapped = data.byteswap().view(data.dtype.newbyteorder())

    out_filename = "SE_" + os.path.basename(filename)
    with open(out_filename, 'wb') as f:
        data_swapped.tofile(f)

    print(f"Converted file saved as {out_filename}")

if __name__ == "__main__":
    main()