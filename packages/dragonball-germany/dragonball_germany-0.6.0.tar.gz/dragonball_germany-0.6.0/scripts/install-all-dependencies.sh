#!/bin/bash -e

if [ -d 'venv' ]; then
    . venv/bin/activate
    . ./scripts/install-dependencies.sh
    . ./scripts/install-dev-dependencies.sh
else
    echo 'There is no virtual environment (venv).'
fi
