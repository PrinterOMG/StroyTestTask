#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# Here can be other setup logic

# Evaluating passed command:
exec "$@"
