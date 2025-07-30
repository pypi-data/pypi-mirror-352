import argparse
import subprocess
import os

"""
Check if a binary file contains debug symbols.

Args:
    binary_path (str): The path to the binary file.

Returns:
    bool: True if the binary contains debug symbols, False otherwise.
"""
def has_debug_symbols(binary_path):
    try:
        result = subprocess.run(['readelf', '-S', binary_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running readelf: {e}")
        return False

    return any('.debug' in line for line in result.stdout.decode().split('\n'))

"""
Strip debug symbols from a binary file and save them in a separate .debug file.

Args:
    binary_path (str): The path to the binary file.
"""
def strip_debug_symbols(binary_path):

    # Get the base name of the binary path
    base_name = os.path.basename(binary_path)

    # Remove the extension
    file_name, file_extension = os.path.splitext(base_name)

    # Now file_name contains the name of the file without the extension
    debug_file = file_name + '.debug'

    try:
        os.chdir(os.path.dirname(binary_path))
        subprocess.run(['objcopy', '--only-keep-debug', base_name, debug_file], check=True)
        subprocess.run(['strip', '--strip-debug', '--strip-unneeded', base_name], check=True)
        subprocess.run(['objcopy', '--add-gnu-debuglink=' + debug_file, base_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stripping debug symbols: {e}")

"""
Main function that checks if a binary file contains debug symbols and strips them if it does.
"""
def main():
    parser = argparse.ArgumentParser(description='Strip debug symbols from a binary file.')
    parser.add_argument('binary_path', help='The path to the binary file.')

    args = parser.parse_args()

    # print (f'Checking {args.binary_path} for debug symbols')

    if not os.path.isfile(args.binary_path):
        print(f'Error: {args.binary_path} does not exist or is not a file')
        return

    if has_debug_symbols(args.binary_path):
        # print info message
        print (f'Stripping CXX object {args.binary_path}')
        strip_debug_symbols(args.binary_path)

if __name__ == '__main__':
    main()