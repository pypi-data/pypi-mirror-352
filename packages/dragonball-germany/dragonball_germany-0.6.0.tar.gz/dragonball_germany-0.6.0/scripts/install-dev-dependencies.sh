#!/bin/bash -e

if [ -d 'venv' ]; then
    . venv/bin/activate
    pip install -r 'requirements-dev.txt'
else
    echo 'There is no virtual environment (venv).'
fi
