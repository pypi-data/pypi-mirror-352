#!/bin/bash

PYPROJECT_FILE="pyproject.toml"

extract_single_line_dependencies() {
    grep -A 1000 "$1" "$PYPROJECT_FILE" | grep -m 1 -B 100 "]" | grep -oP "(?<=\[').*?(?='\])"
}

extract_multi_line_dependencies() {
    grep -A 1000 "$1" "$PYPROJECT_FILE" | grep -m 1 -B 100 "\]" | grep -v "\[" | tr -d "]', "
}

handle_dependencies() {
    local section=$1
    local requirements_file=$2

    dependencies=$(extract_multi_line_dependencies "$section")
    if [[ -z "$dependencies" ]]; then
        dependencies=$(extract_single_line_dependencies "$section")
        if [[ -z "$dependencies" ]]; then
             rm -f "$requirements_file"
             return
        fi
    fi

    if [[ $dependencies =~ "', '" ]]; then
        dependencies="${dependencies//\', \'/$'\n'}"
    fi

    echo "$dependencies" > "$requirements_file"
}

handle_dependencies "dependencies = \[" "requirements.txt"
handle_dependencies "dev = \[" "requirements-dev.txt"
