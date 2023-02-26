#!/bin/sh -e
set -x

black . --line-length=120
ruff clean
ruff --fix .
mypy --check-untyped-defs -p app