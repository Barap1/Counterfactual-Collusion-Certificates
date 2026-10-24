#!/bin/sh
# Run from repo root after the final DEV command finishes. Offline, $0.
set -eu
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/scripts/offline_guard:$PWD"
BENCH_PY=starter/collusion_hackathon/colosseum/.venv/bin/python
"$BENCH_PY" -m ccc.bench report --run docs/enh/bench/dev_run > docs/enh/bench/align2_report.log 2>&1
"$BENCH_PY" -m ccc.bench hashes > docs/enh/bench/hash_manifest.json
"$BENCH_PY" docs/enh/bench/verify_run.py > docs/enh/bench/align2_verification.log 2>&1
"$BENCH_PY" docs/enh/bench/compare_align2.py > docs/enh/bench/align2_delta.log 2>&1
python3 -I demo/build_twins.py --run docs/enh/bench/dev_run --label DEV --dev-run docs/enh/bench/dev_run > docs/enh/bench/align2_demo_twins.log 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python demo/explorer/bundle_data.py > docs/enh/bench/align2_demo_bundle.log 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python demo/build_data.py > docs/enh/bench/align2_demo_data.log 2>&1
"$BENCH_PY" docs/enh/bench/align2_figure_smoke.py > docs/enh/bench/align2_figure_smoke.log 2>&1
"$BENCH_PY" -m unittest tests.test_bench_core tests.test_bench_alignment > docs/enh/bench/align2_targeted_tests.log 2>&1
"$BENCH_PY" docs/enh/bench/run_tests.py > docs/enh/bench/align2_offline_suite.log 2>&1
"$BENCH_PY" docs/enh/bench/align2_checks.py > docs/enh/bench/align2_final_checks.log 2>&1
git diff --check -- ccc/bench tests/test_bench_alignment.py docs/enh/bench ops/reports/BENCH-ALIGN2.md
