#!/bin/sh

set -x
set -e

black --check src
isort --check src
mypy src
flake8 src
