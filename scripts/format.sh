#!/bin/sh -e
set -x

ruff --fix .
black .