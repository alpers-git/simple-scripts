#!/usr/bin/env python3
"""
Convert TIF image stack to VTK format.

This script reads a TIF file containing a stack of images representing a 3D volume
and converts it to VTK (Visualization Toolkit) format.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import imageio


def read_tif_stack(tif_path):
    """
    Read a TIF file containing a stack of images.
    
    Args:
        tif_path: Path to the TIF file
        
    Returns:
        numpy array with shape (depth, height, width) or (depth, height, width, channels)
    """
    try:
        # Try using imageio first (handles multi-page TIFF files well)
        volume = imageio.volread(tif_path)
        print(f"Loaded TIF stack with shape: {volume.shape}")
        print(f"Data type: {volume.dtype}")
        print(f"Min value: {volume.min()}, Max value: {volume.max()}")
        return volume
    except Exception as e:
        print(f"Error reading TIF file with imageio: {e}")
        print("Trying alternative method with PIL...")
        
        # Fallback to PIL
        try:
            img = Image.open(tif_path)
            frames = []
            
            # Read all frames in the stack
            try:
                while True:
                    frames.append(np.array(img))
                    img.seek(img.tell() + 1)
            except EOFError:
                pass  # End of sequence
            
            volume = np.array(frames)
            print(f"Loaded TIF stack with shape: {volume.shape}")
            print(f"Data type: {volume.dtype}")
            print(f"Min value: {volume.min()}, Max value: {volume.max()}")
            return volume
        except Exception as e:
            print(f"Error reading TIF file: {e}")
            sys.exit(1)


def deskew_volume(volume, offset_x_per_z):
    """
    Deskew a 3D volume by shifting each z-slice in the x direction.
    
    Args:
        volume: 3D numpy array with shape (depth, height, width)
        offset_x_per_z: Number of pixels to shift in x direction per z slice
        
    Returns:
        Deskewed 3D numpy array
    """
    z, y, x = volume.shape
    # Calculate new x dimension after deskewing
    nx = int(x + (offset_x_per_z * (z - 1)))
    
    # Create new volume with expanded x dimension
    deskewed = np.zeros((z, y, nx), dtype=volume.dtype)
    
    # Shift each z-slice by the appropriate offset
    for i in range(z):
        base = int(i * offset_x_per_z)
        deskewed[i, :, base:base + x] = volume[i, :, :]
    
    print(f"Deskewed volume from {x}x{y}x{z} to {nx}x{y}x{z}")
    return deskewed


def write_vtk(volume, output_path, spacing=(1.0, 1.0, 1.0), binary=True):
    """
    Write volume data to VTK format (legacy format, binary or ASCII).
    
    Args:
        volume: 3D numpy array with shape (depth, height, width)
        output_path: Path to output VTK file
        spacing: Tuple of (x, y, z) spacing between voxels
        binary: If True, write binary format (faster, smaller); if False, write ASCII
    """
    # Handle multi-channel images by converting to grayscale if needed
    if len(volume.shape) == 4:
        print(f"Multi-channel image detected. Converting to grayscale...")
        # Convert RGB to grayscale using standard weights
        if volume.shape[3] == 3:
            volume = np.dot(volume[..., :3], [0.299, 0.587, 0.114])
        elif volume.shape[3] == 4:
            # RGBA - ignore alpha channel
            volume = np.dot(volume[..., :3], [0.299, 0.587, 0.114])
        else:
            # Take first channel
            volume = volume[..., 0]
    
    depth, height, width = volume.shape
    print(f"Volume shape for VTK: depth={depth}, height={height}, width={width}")
    
    # Normalize data to appropriate range if needed
    if volume.dtype == np.uint8:
        data_array = volume.copy()
        scalar_type = "unsigned_char"
    elif volume.dtype == np.uint16:
        data_array = volume.copy()
        scalar_type = "unsigned_short"
    elif volume.dtype == np.float32 or volume.dtype == np.float64:
        # Keep as float for better precision
        data_array = volume.astype(np.float32)
        scalar_type = "float"
    else:
        # Normalize to 0-255 range for other types
        data_min = float(volume.min())
        data_max = float(volume.max())
        if data_max > data_min:
            data_array = ((volume.astype(np.float64) - data_min) / (data_max - data_min) * 255).astype(np.uint8)
        else:
            data_array = np.zeros_like(volume, dtype=np.uint8)
        scalar_type = "unsigned_char"
    
    if binary:
        # Write binary VTK file
        with open(output_path, 'wb') as f:
            # Write ASCII header
            header = "# vtk DataFile Version 3.0\n"
            header += "TIF to VTK conversion\n"
            header += "BINARY\n"
            header += "DATASET STRUCTURED_POINTS\n"
            header += f"DIMENSIONS {width} {height} {depth}\n"
            header += f"SPACING {spacing[0]:.6f} {spacing[1]:.6f} {spacing[2]:.6f}\n"
            header += "ORIGIN 0.0 0.0 0.0\n"
            
            num_points = width * height * depth
            header += f"POINT_DATA {num_points}\n"
            header += f"SCALARS image_data {scalar_type} 1\n"
            header += "LOOKUP_TABLE default\n"
            
            f.write(header.encode('ascii'))
            
            # VTK expects data in (z, y, x) order with x varying fastest
            # Our data is (depth, height, width) which is (z, y, x)
            # We need to transpose to (x, y, z) ordering, then flatten with C order
            # Actually, we need to reorder from (z,y,x) to have x vary fastest
            data_reordered = np.transpose(data_array, (0, 1, 2))  # Keep as (z, y, x)
            data_flat = data_reordered.flatten(order='C')  # Flatten with x varying fastest
            
            # Write data in big-endian format (VTK standard)
            if scalar_type == "unsigned_char":
                f.write(data_flat.astype('>u1').tobytes())
            elif scalar_type == "unsigned_short":
                f.write(data_flat.astype('>u2').tobytes())
            elif scalar_type == "float":
                f.write(data_flat.astype('>f4').tobytes())
    else:
        # Write ASCII VTK file
        with open(output_path, 'w') as f:
            # Header
            f.write("# vtk DataFile Version 3.0\n")
            f.write("TIF to VTK conversion\n")
            f.write("ASCII\n")
            f.write("DATASET STRUCTURED_POINTS\n")
            
            # Dimensions (width, height, depth in VTK format)
            f.write(f"DIMENSIONS {width} {height} {depth}\n")
            
            # Spacing between points
            f.write(f"SPACING {spacing[0]:.6f} {spacing[1]:.6f} {spacing[2]:.6f}\n")
            
            # Origin
            f.write("ORIGIN 0.0 0.0 0.0\n")
            
            # Point data
            num_points = width * height * depth
            f.write(f"POINT_DATA {num_points}\n")
            f.write(f"SCALARS image_data {scalar_type} 1\n")
            f.write("LOOKUP_TABLE default\n")
            
            # VTK expects data in (z, y, x) order with x varying fastest
            # Our data is (depth, height, width) which is (z, y, x)
            data_reordered = np.transpose(data_array, (0, 1, 2))  # Keep as (z, y, x)
            data_flat = data_reordered.flatten(order='C')  # Flatten with x varying fastest
            
            # Write data values
            for value in data_flat:
                if scalar_type == "float":
                    f.write(f"{value:.6f}\n")
                else:
                    f.write(f"{int(value)}\n")
    
    print(f"VTK file written to: {output_path}")
    print(f"Format: {'Binary' if binary else 'ASCII'}")
    print(f"Data type: {scalar_type}")
    print(f"Dimensions: {width} x {height} x {depth}")
    print(f"Spacing: {spacing}")


def process_single_file(input_path, output_path, spacing, binary, deskew_offset):
    """
    Process a single TIF file and convert it to VTK.
    
    Args:
        input_path: Path to input TIF file
        output_path: Path to output VTK file
        spacing: Tuple of (x, y, z) voxel spacing
        binary: Whether to write binary format
        deskew_offset: Deskew offset value (None if no deskewing)
    """
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    
    # Read TIF stack
    print("\nReading TIF stack...")
    volume = read_tif_stack(input_path)
    
    # Apply deskewing if requested
    if deskew_offset is not None:
        print(f"\nApplying deskewing with offset_x_per_z = {deskew_offset}...")
        volume = deskew_volume(volume, deskew_offset)
    
    # Write VTK file
    print("\nWriting VTK file...")
    write_vtk(volume, output_path, spacing=spacing, binary=binary)
    
    print("\nConversion complete!")


def main():
    parser = argparse.ArgumentParser(
        description='Convert TIF image stack to VTK format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tif2VTK.py input.tif
  python tif2VTK.py input.tif -o output.vtk
  python tif2VTK.py input.tif -s 1.0 1.0 2.0
  python tif2VTK.py input.tif --ascii
  python tif2VTK.py input.tif -dskw 7
  python tif2VTK.py /path/to/directory/
        """
    )
    
    parser.add_argument('input', type=str, help='Input TIF file path or directory containing TIF files')
    parser.add_argument('-o', '--output', type=str, help='Output VTK file path (default: input_name.vtk) or output directory when processing multiple files')
    parser.add_argument('-s', '--spacing', type=float, nargs=3, default=[1.0, 1.0, 1.0],
                        metavar=('X', 'Y', 'Z'),
                        help='Voxel spacing in X, Y, Z directions (default: 1.0 1.0 1.0)')
    parser.add_argument('--ascii', action='store_true',
                        help='Write ASCII format instead of binary (binary is default)')
    parser.add_argument('-dskw', '--deskew', type=float, metavar='OFFSET',
                        help='Deskew the volume with specified offset_x_per_z (e.g., 7)')
    
    args = parser.parse_args()
    
    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)
    
    # Check if input is a directory or a file
    if input_path.is_dir():
        # Process all TIF files in the directory
        print(f"Processing directory: {input_path}")
        
        # Find all TIF files
        tif_files = list(input_path.glob('*.tif')) + list(input_path.glob('*.tiff'))
        
        if not tif_files:
            print(f"Error: No TIF files found in directory '{input_path}'")
            sys.exit(1)
        
        print(f"Found {len(tif_files)} TIF file(s) to process\n")
        
        # Determine output directory
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = input_path
        
        # Process each file
        for i, tif_file in enumerate(tif_files, 1):
            print(f"\n{'='*80}")
            print(f"Processing file {i}/{len(tif_files)}: {tif_file.name}")
            print(f"{'='*80}")
            
            output_file = output_dir / tif_file.with_suffix('.vtk').name
            
            try:
                process_single_file(
                    tif_file, 
                    output_file, 
                    tuple(args.spacing), 
                    not args.ascii, 
                    args.deskew
                )
            except Exception as e:
                print(f"Error processing {tif_file.name}: {e}")
                continue
        
        print(f"\n{'='*80}")
        print(f"Batch processing complete! Processed {len(tif_files)} file(s)")
        print(f"{'='*80}")
    
    else:
        # Process single file
        if not input_path.is_file():
            print(f"Error: Input path '{args.input}' is not a valid file.")
            sys.exit(1)
        
        # Determine output file path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.vtk')
        
        process_single_file(
            input_path, 
            output_path, 
            tuple(args.spacing), 
            not args.ascii, 
            args.deskew
        )


if __name__ == "__main__":
    main()
