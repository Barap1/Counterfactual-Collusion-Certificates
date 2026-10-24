#!/bin/zsh
set -eu
cd "${0:A:h:h}"
export CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/scripts/offline_guard:$PWD"
PY=starter/collusion_hackathon/colosseum/.venv/bin/python
[[ -x "$PY" ]] || { print -u2 'Complete README starter setup first'; exit 1; }
OUT=$(mktemp -d "$PWD/docs/release/reproduction.XXXXXX")
print "Evidence: $OUT"
nice -n 19 "$PY" -m tests.replay.offline_runner -s tests -t . > "$OUT/tests.log" 2>&1
nice -n 19 "$PY" scripts/reproduce_offline.py "$OUT" > "$OUT/reproduction.log" 2>&1
print "Reproduction verified: $OUT"
