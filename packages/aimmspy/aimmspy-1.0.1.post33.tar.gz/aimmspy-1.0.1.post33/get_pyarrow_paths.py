import pyarrow as pa
import os
import json
import argparse
import platform

def library_file_check( library_name ):
    if platform.system().lower() == 'linux':
        return library_name.endswith('.so')
    elif platform.system().lower() == 'windows':
        return library_name.endswith('.dll')
    else:
        raise ValueError("Unsupported platform")

def get_library_files(library_dirs, library_names):
    """Find all library files matching the given library names in the specified directories."""
    library_files = []
    for library_dir in library_dirs:
        for root, _, files in os.walk(library_dir):
            for file in files:
                base_name = os.path.basename(file).split('.')[0]
                if base_name in [name.split('.')[0] for name in library_names]:
                    library_files.append(os.path.join(root, file))
    # Remove duplicates and filter for .so files
    return list(set(file for file in library_files if library_file_check(file)))

def format_paths_for_output(paths):
    """Format paths for JSON output by replacing backslashes with forward slashes."""
    return '@'.join(path.replace('\\', '/') for path in paths)

def write_pyarrow_paths_to_file(output_path, include_dir, library_dirs, library_names, library_files):
    """Write the pyarrow paths information to a JSON file."""
    with open(os.path.join(output_path, 'pyarrow_paths.json'), 'w') as file:
        json.dump(
            {
                'includes': include_dir,
                'library_dirs': library_dirs,
                'libraries': library_names,
                'to_copy_list': library_files
            },
            file
        )

def main(args):
    library_names = pa.get_libraries()
    library_dirs = pa.get_library_dirs()
    include_dir = pa.get_include()
    pa.create_library_symlinks()

    if platform.system().lower() == 'linux':
        library_names = [f'lib{lib}' for lib in library_names]
        library_names += ['libarrow_substrait', 'libarrow_dataset', 'libarrow_acero', 'libparquet']
        library_files = get_library_files(library_dirs, library_names)
        library_names = [f'{lib}.so' for lib in library_names]
    elif platform.system().lower() == 'windows':
        library_names = [f'{lib}.dll' for lib in library_names]
        library_names += ['arrow_substrait.dll', 'arrow_dataset.dll', 'arrow_acero.dll', 'parquet.dll']
        library_files = get_library_files(library_dirs, library_names)
    else:
        library_files = []

    formatted_library_dirs = format_paths_for_output(library_dirs)
    formatted_library_names = format_paths_for_output(library_names)
    formatted_library_files = format_paths_for_output(library_files)
    formatted_include_dir = include_dir.replace('\\', '/')

    write_pyarrow_paths_to_file(
        args.path,
        formatted_include_dir,
        formatted_library_dirs,
        formatted_library_names,
        formatted_library_files
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to write the pyarrow paths', default=os.getcwd())
    args = parser.parse_args()
    main(args)