#!/bin/bash -e

if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit is not installed."
    return
fi

pre-commit run --all-files
