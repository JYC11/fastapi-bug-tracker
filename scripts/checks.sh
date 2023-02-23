#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --expand-star-imports --exclude=__init__.py
isort --line-length 120 .
black --line-length 120 .
flake8 --max-line-length 120 .
mypy -p app