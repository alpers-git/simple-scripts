import os
import sys
import glob
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


def stack_tifs_to_raw(prefix_path, out_path=None, glob_pattern=None):
	"""Stack all TIFF files with a given prefix into a raw volume.

	Args:
		prefix_path: Path to a file prefix or directory+prefix. Examples:
			'/path/to/prefix' will match files like '/path/to/prefix0001.tif'
			'/path/to/dir/prefix' or 'prefix' (current dir).
		out_path: Optional output path. If None, will be created next to prefix with naming
			'<prefix>_XxYxZ_<dtype>.raw'.
		glob_pattern: Optional glob pattern to find files. If None, the function will
			try common suffixes: '<prefix>*.tif', '<prefix>*.tiff'.

	Returns:
		The path to the written raw file.
	"""
	# Resolve directory and prefix
	prefix_dir = os.path.dirname(prefix_path) or '.'
	prefix_base = os.path.basename(prefix_path)

	# Build file list
	if glob_pattern:
		pattern = os.path.join(prefix_dir, glob_pattern)
		files = sorted(glob.glob(pattern))
	else:
		patterns = [f"{prefix_base}*.tif", f"{prefix_base}*.tiff"]
		files = []
		for p in patterns:
			files.extend(sorted(glob.glob(os.path.join(prefix_dir, p))))

	if not files:
		raise FileNotFoundError(f"No TIFF files found for prefix '{prefix_path}'")

	# Read first image to get shape and dtype
	first = tifffile.imread(files[0])
	color_to_gray = False
	if first.ndim == 2:
		height, width = first.shape
		dtype = first.dtype
	elif first.ndim == 3 and first.shape[-1] in (3, 4):
		# Color image: convert to grayscale using luminosity method
		color_to_gray = True
		height, width = first.shape[:2]
		dtype = first.dtype
		print("Note: color TIFFs detected. Converting to grayscale using luminosity method.")
	else:
		raise ValueError(f"Unsupported image shape in file {files[0]}: {first.shape}")

	# Create empty volume: depth x height x width
	depth = len(files)
	volume = np.empty((depth, height, width), dtype=dtype)

	# Precompute weights for luminosity conversion (R,G,B)
	weights = np.array([0.2989, 0.5870, 0.1140], dtype=np.float32)

	# Fill volume
	for i, f in enumerate(files):
		img = tifffile.imread(f)
		# Handle color images by converting to grayscale if needed
		if img.ndim == 3 and img.shape[-1] in (3, 4):
			if not color_to_gray:
				# This shouldn't happen since we checked the first file, but be safe
				raise ValueError(f"Found color image in file {f}; only single-channel TIFFs supported")
			# drop alpha channel if present and compute luminosity
			rgb = img[..., :3].astype(np.float32)
			gray = np.tensordot(rgb, weights, axes=([-1], [0]))
			# Clip and cast back to original dtype
			if np.issubdtype(dtype, np.integer):
				info = np.iinfo(dtype)
				gray = np.rint(np.clip(gray, info.min, info.max)).astype(dtype)
			else:
				# float types
				gray = gray.astype(dtype)
			img = gray
		if img.shape != (height, width):
			raise ValueError(f"Image {f} has shape {img.shape} but expected {(height, width)}")
		if img.dtype != dtype:
			img = img.astype(dtype)
		volume[i, ...] = img

	# Compose output filename if not provided
	if out_path is None:
		dtype_str = get_datatype_str(dtype)
		base = prefix_base
		out_name = f"{base}_{width}x{height}x{depth}_{dtype_str}.raw"
		out_path = os.path.join(prefix_dir, out_name)

	save_raw_volume(volume, out_path, dtype)
	return out_path


def _cli():
	if len(sys.argv) < 2 or len(sys.argv) > 4:
		print("Usage: python tifstack2raw.py <prefix_path> [out_path] [glob_pattern]")
		print("Example: python tifstack2raw.py ./slice_ ./stack.raw 'slice_*.tif'")
		sys.exit(1)
	prefix = sys.argv[1]
	out = sys.argv[2] if len(sys.argv) >= 3 else None
	g = sys.argv[3] if len(sys.argv) == 4 else None
	out_file = stack_tifs_to_raw(prefix, out_path=out, glob_pattern=g)
	print(f"Saved raw volume: {out_file}")


if __name__ == '__main__':
	_cli()

