import numpy as np

def generate_3d_custom_direction_grid(size, direction, output_file):
    # Create a 3D array with a gradient in the specified direction
    if direction.lower() == 'x':
        values = np.linspace(1.0, 0.0, size, dtype=np.float32)
        scalar_values = np.outer(values, np.ones((size, size), dtype=np.float32)).transpose()
    elif direction.lower() == '-x':
        values = np.linspace(0.0, 1.0, size, dtype=np.float32)
        scalar_values = np.outer(values, np.ones((size, size), dtype=np.float32)).transpose()
    elif direction.lower() == 'y':
        values = np.linspace(1.0, 0.0, size, dtype=np.float32)
        y, z = np.meshgrid(values, np.linspace(0, 1, size))
        scalar_values = np.tile(y[:, :, np.newaxis], (1, 1, size))
    elif direction.lower() == '-y':
        values = np.linspace(0.0, 1.0, size, dtype=np.float32)
        y, z = np.meshgrid(values, np.linspace(0, 1, size))
        scalar_values = np.tile(y[:, :, np.newaxis], (1, 1, size))
    elif direction.lower() == 'z':
        values = np.linspace(1.0, 0.0, size, dtype=np.float32)
        scalar_values = np.outer(values, np.ones((size, size), dtype=np.float32))
    elif direction.lower() == '-z':
        values = np.linspace(0.0, 1.0, size, dtype=np.float32)
        scalar_values = np.outer(values, np.ones((size, size), dtype=np.float32))
    else:
        print("Invalid direction. Please enter 'X', 'Y', or 'Z'.")
        return

    # Scale the gradient to fit the 8-bit range
    scalar_values = (scalar_values * 255).astype(np.uint8)

    # Save the 3D array to a binary file
    with open(output_file, 'wb') as file:
        file.write(scalar_values.tobytes())

# Get user input for grid dimensions and direction
size = int(input("Enter the size of the grid: "))
direction = input("Enter the direction (X, Y, or Z) in which values will decrease: ")
output_file = input("Enter the output file name: ")

# Generate and save the 3D gradient grid in the specified direction
generate_3d_custom_direction_grid(size, direction, output_file)
