#!/bin/sh

set -x
set -e

black src
isort --profile black src
