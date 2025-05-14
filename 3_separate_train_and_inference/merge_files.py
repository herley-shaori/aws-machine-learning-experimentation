import json
import os
import glob
from pathlib import Path


def read_paths_and_filters(json_file):
    if os.path.exists(json_file):
        print(f"Found {json_file}, reading contents...")
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"Paths from JSON: {data['paths']}")
        print(f"Filters from JSON: {data['filters']}")
        return data['paths'], data['filters']
    else:
        print(f"{json_file} not found, using default paths and filters.")
        default_paths = ['*']
        default_filters = ['*.yml', '*.yaml', '*.py', '*.json', '*.txt', '*.sh']
        print(f"Default paths: {default_paths}")
        print(f"Default filters: {default_filters}")
        return default_paths, default_filters


def get_files_from_patterns(paths, filters):
    matched_files = []
    print(f"Scanning paths: {paths}")
    for path in paths:
        print(f"Processing path: {path}")
        # Expand wildcard patterns
        if '*' in path:
            for file in glob.glob(path, recursive=True):
                if is_valid_file(file, filters):
                    print(f"Matched file: {file}")
                    matched_files.append(file)
        else:
            if is_valid_file(path, filters):
                print(f"Matched file: {path}")
                matched_files.append(path)
    print(f"Total matched files: {len(matched_files)}")
    return matched_files


def is_valid_file(file_path, filters):
    # Skip .venv directories
    if '.venv' in file_path:
        print(f"Skipping .venv path: {file_path}")
        return False
    # Check if file matches any filter
    is_valid = any(file_path.endswith(ext.lstrip('*')) for ext in filters) and os.path.isfile(file_path)
    print(f"Checking file: {file_path}, Valid: {is_valid}")
    return is_valid


def merge_files(files, output_file):
    print(f"Writing to {output_file}")
    with open(output_file, 'w') as outfile:
        if not files:
            print("No files to merge.")
            outfile.write("No files matched the specified paths and filters.\n")
        for file in files:
            print(f"Reading file: {file}")
            outfile.write(f"\n\n--- {file} ---\n\n")
            try:
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
            except Exception as e:
                outfile.write(f"Error reading file: {e}\n")


def main():
    json_file = 'paths.json'
    output_file = 'output.txt'

    print(f"Current working directory: {os.getcwd()}")

    # Read paths and filters from JSON or use defaults
    paths, filters = read_paths_and_filters(json_file)

    # Get all matching files
    files = get_files_from_patterns(paths, filters)

    # Merge files into output.txt
    merge_files(files, output_file)
    print(f"Files merged into {output_file}")


if __name__ == "__main__":
    main()