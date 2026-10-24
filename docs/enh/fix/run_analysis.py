"""Authorized held-out rerun with network/secret guard; no extraction."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.replay.offline_runner import guard
sys.addaudithook(guard)
from ccc.analysis.pipeline import run
raise SystemExit(run('docs/runner/exp002-live', 'docs/analysis/exp002_heldout_v3',
                     watchdog_dir='docs/runner/exp002-live.watchdog'))
