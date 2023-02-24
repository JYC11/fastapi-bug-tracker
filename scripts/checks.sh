#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --expand-star-imports --exclude=__init__.py
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 app --count --exit-zero --max-line-length=120 --statistics
black app
isort --profile black app
mypy --check-untyped-defs -p app