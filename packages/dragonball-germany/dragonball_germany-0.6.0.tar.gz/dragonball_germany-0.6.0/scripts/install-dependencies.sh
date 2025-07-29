#!/bin/bash -e

if [ -d 'venv' ]; then
    source venv/bin/activate
    pip install -r 'requirements.txt'
else
    echo 'There is no virtual environment (venv).'
fi
