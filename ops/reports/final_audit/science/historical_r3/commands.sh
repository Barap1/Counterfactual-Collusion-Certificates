# Run from /Users/aarav/Documents/Projects/ApartSprint.
# Independent analysis and provenance checks (standard library; no ccc imports):
PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/ccc-W1-R3/audit.py > /private/tmp/ccc-W1-R3/audit.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/ccc-W1-R3/provenance.py > /private/tmp/ccc-W1-R3/provenance.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/ccc-W1-R3/compare.py > /private/tmp/ccc-W1-R3/comparison.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/ccc-W1-R3/schedule.py > /private/tmp/ccc-W1-R3/schedule.log 2>&1
# Copy creation was executed once before report generation:
# python3 heredoc: shutil.copytree(Path('docs/enh/r2/run_par'), Path('/private/tmp/ccc-W1-R3/run_par_copy'))
# Frozen report cross-check; original run directory is NOT the target:
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench report --run /private/tmp/ccc-W1-R3/run_par_copy > /private/tmp/ccc-W1-R3/frozen_report.log 2>&1
# Read-only inspection used cat, sed, rg, nl, ls, du and Python JSON/gzip/hashlib queries.
# A process-inspection command (ps piped to rg) was denied by the sandbox; no data resulted.
