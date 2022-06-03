#!/bin/sh

set -x
set -e

black --check tests
isort --check tests
mypy tests
flake8 tests
