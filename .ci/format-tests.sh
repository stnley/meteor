#!/bin/sh

set -x
set -e

black tests
isort --profile black tests
