import os
import sys
import numpy as np
import tifffile

# Mapping numpy dtype to string for filename
DTYPE_MAP = {
    np.dtype('uint8'): 'uint8',
    np.dtype('int8'): 'char',
    np.dtype('uint16'): 'uint16',
    np.dtype('int16'): 'int16',
    np.dtype('uint32'): 'uint',
    np.dtype('int32'): 'int',
    np.dtype('float32'): 'float32',
    np.dtype('float64'): 'double64'
}

def get_datatype_str(dtype):
    """Return string representation for filename based on dtype."""
    return DTYPE_MAP.get(dtype, str(dtype))

def save_raw_volume(volume, out_path, dtype):
    """Save numpy volume to raw file in little-endian order."""
    # Ensure little-endian byte order if applicable
    if volume.dtype.byteorder not in ('<', '|'):
        volume = volume.byteswap().view(volume.dtype.newbyteorder('<'))
    volume.astype(dtype).tofile(out_path)

def main(tif_path):
    # Load the TIFF stack
    volume = tifffile.imread(tif_path)
    # Ensure it's at least 3D
    if volume.ndim == 2:
        volume = volume[np.newaxis, ...]
    elif volume.ndim == 4:
        # If shape is (z, y, x, c), drop channel or raise
        if volume.shape[-1] == 1:
            volume = volume[..., 0]
        else:
            raise ValueError("4D TIFF stacks with multiple channels are not supported.")

    # Get dimensions
    dim_z, dim_y, dim_x = volume.shape

    # Get data type string
    dtype_str = get_datatype_str(volume.dtype)
    if dtype_str is None:
        raise ValueError(f"Unsupported data type: {volume.dtype}")

    # Compose output filename
    base = os.path.splitext(os.path.basename(tif_path))[0]
    out_name = f"{base}_{dim_x}x{dim_y}x{dim_z}_{dtype_str}.raw"
    out_path = os.path.join(os.path.dirname(tif_path), out_name)

    # Write raw file
    save_raw_volume(volume, out_path, volume.dtype)

    print(f"Saved raw volume: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tif_to_raw.py <input_stack.tif>")
        sys.exit(1)
    main(sys.argv[1])
