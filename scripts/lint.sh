#!/usr/bin/env bash

set -x

ruff --fix .
black app --check
mypy -p app