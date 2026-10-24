#!/bin/zsh
set -eu
cd "${0:A:h:h}"
# .env is read only inside this scanner; no value or matching content is emitted.
exec nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python scripts/secret_scan.py "$@"
