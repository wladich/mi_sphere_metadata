#!/bin/bash

set -e

BASE="$(dirname $0)"
cd "$BASE"

echo 'pylint...'
pylint ./*.py tests/*.py
echo 'Black...'
black --diff --check -q ./*.py tests/*.py
echo 'flake8...'
flake8 *.py tests/*.py
echo 'mypy...'
mypy

echo All checks passed.
