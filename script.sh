#!/bin/bash

# Function to check if a file matches any filter
matches_filter() {
    local file="$1"
    shift
    local filters=("$@")
    local ext="${file##*.}"

    for filter in "${filters[@]}"; do
        # Clean filter to handle *.yaml, .yaml, or yaml
        filter_clean="${filter##*.}"
        filter_clean="${filter_clean#\.}"
        if [[ "$ext" == "$filter_clean" ]]; then
            echo "Debug: File $file matches filter $filter (ext: $ext, filter_clean: $filter_clean)" >&2
            return 0
        fi
    done
    echo "Debug: File $file does not match any filter (ext: $ext)" >&2
    return 1
}

# Function to generate path output
generate_path_output() {
    local config_path="$1"
    local output_file="path_output.txt"

    # Check if config file exists
    if [[ ! -f "$config_path" ]]; then
        echo "Error: Config file $config_path not found" >&2
        return 1
    fi

    # Read paths and filters from JSON using jq
    paths=()
    while IFS= read -r path; do
        paths+=("$path")
    done < <(jq -r '.paths[]' "$config_path")

    filters=()
    while IFS= read -r filter; do
        filters+=("$filter")
    done < <(jq -r '.filters[]' "$config_path")

    # Debugging: Print paths and filters
    echo "Debug: Paths = ${paths[*]}" >&2
    echo "Debug: Filters = ${filters[*]}" >&2

    # Initialize output content
    output_content=""

    # Process each path pattern
    for pattern in "${paths[@]}"; do
        # Extract directory from pattern
        dir="${pattern%/*}"
        if [[ "$dir" == "$pattern" ]]; then
            dir="."
        fi
        echo "Debug: Searching in directory $dir with pattern $pattern" >&2
        echo "Debug: Running find command: find ./$dir -maxdepth 1 -type f" >&2

        # Find files in the specified directory
        while IFS= read -r file; do
            if [[ -f "$file" && -r "$file" ]]; then
                echo "Debug: Found readable file $file" >&2
                # Check if file matches any filter
                if matches_filter "$file" "${filters[@]}"; then
                    # Read file content
                    content=$(cat "$file" 2>/dev/null)
                    if [[ $? -eq 0 ]]; then
                        echo "Debug: Adding $file to output" >&2
                        output_content+="$file\n$content\n\n"
                    else
                        echo "Debug: Failed to read content of $file" >&2
                    fi
                fi
            else
                echo "Debug: Skipping $file (not a file or not readable)" >&2
            fi
        done < <(find "./$dir" -maxdepth 1 -type f 2>/dev/null)
    done

    # Write output to file, trimming trailing newlines
    if [[ -n "$output_content" ]]; then
        printf "%s" "$output_content" | awk 'NR > 1 {print prev} {prev=$0}' > "$output_file"
        if [[ $? -eq 0 ]]; then
            echo "Successfully generated $output_file"
        else
            echo "Error writing to $output_file" >&2
            return 1
        fi
    else
        echo "Warning: No matching files found, created empty $output_file" >&2
        touch "$output_file"
    fi
}

# Main execution
main() {
    # Check if jq is installed
    if ! command -v jq >/dev/null 2>&1; then
        echo "Error: jq is required but not installed" >&2
        exit 1
    fi

    # Run the generation with paths.json
    generate_path_output "paths.json"
}

# Execute main
main