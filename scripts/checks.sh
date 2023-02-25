#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --expand-star-imports --exclude=__init__.py
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-line-length=120 --statistics
black .
isort --profile black .
mypy --check-untyped-defs -p app