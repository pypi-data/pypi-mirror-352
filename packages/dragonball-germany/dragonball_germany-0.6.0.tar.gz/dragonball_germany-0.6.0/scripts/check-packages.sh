#!/bin/bash -e

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌There is no virtual environment (venv) active."
    return
fi

pip list --outdated
