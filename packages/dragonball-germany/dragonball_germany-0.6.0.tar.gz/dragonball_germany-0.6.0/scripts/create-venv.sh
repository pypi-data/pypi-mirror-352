#!/bin/bash -e

if [ -d 'venv' ]; then
    echo 'The virtual environment (venv) already exists.'
else
    python -m venv venv
fi
