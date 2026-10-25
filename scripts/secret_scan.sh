#!/bin/zsh
set -eu
cd "${0:A:h:h}"
# Standard-library pattern scan; credential files are excluded without reading.
exec nice -n 19 python3 scripts/secret_scan.py "$@"
