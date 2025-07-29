#!/bin/bash -e

if [ -d 'venv' ]; then
    . venv/bin/activate
else
    echo 'There is no virtual environment (venv).'
fi
