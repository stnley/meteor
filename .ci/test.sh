#!/bin/sh

set -e
set -x

pytest --cov tests "${@}"
