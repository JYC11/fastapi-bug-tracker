#!/bin/sh -e
set -x

ruff --fix .
black . --line-length=120
mypy --check-untyped-defs -p app