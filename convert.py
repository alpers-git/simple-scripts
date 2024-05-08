import os
import struct

def convert_file(input_file, entry_count, original_format, target_format):
    formats = {
        'double': ('d', '.d64'),
        'float': ('f', '.f32'),
        'short': ('h', '.s2'),
        'ushort': ('H', '.us2'),
        'int': ('i', '.int32'),
        'uint': ('I', '.uint32')
    }

    if original_format not in formats or target_format not in formats:
        print("Invalid format specified.")
        return

    original_format_char, original_extension = formats[original_format]
    target_format_char, target_extension = formats[target_format]

    output_filename, _ = os.path.splitext(input_file)
    output_filename += "_converted"+ target_extension

    with open(input_file, 'rb') as infile, open(output_filename, 'wb') as outfile:
        for _ in range(entry_count):
            original_value = infile.read(struct.calcsize(original_format_char))
            if not original_value:
                print("End of file reached before reading expected number of entries.")
                return

            unpacked_value = struct.unpack(original_format_char, original_value)[0]
            packed_value = struct.pack(target_format_char, unpacked_value)
            outfile.write(packed_value)

    print("Conversion completed. Output file:", output_filename)

if __name__ == "__main__":
    input_file = input("Enter the path to the input file: ")
    entry_count = int(input("Enter the number of entries: "))
    original_format = input("Enter the original format (double, float, short, ushort, int, uint): ")
    target_format = input("Enter the target format (double, float, short, ushort, int, uint): ")

    convert_file(input_file, entry_count, original_format, target_format)
