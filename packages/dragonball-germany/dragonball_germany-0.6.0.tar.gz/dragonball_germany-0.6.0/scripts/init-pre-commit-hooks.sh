#!/bin/bash -e

pre-commit install
pre-commit install --hook-type commit-msg
