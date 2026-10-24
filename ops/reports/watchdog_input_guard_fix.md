Task: owner-requested watchdog input guard fix
Status: complete; no live calls, no commits, sealed evidence untouched.
Artifacts: ccc/analysis/{loaders.py,__main__.py,pipeline.py,stage2.py}; tests/analysis/test_input_guard.py
Validation command: starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
Additional check: git diff --check
Changes: root, sibling <root>.watchdog, and optional watchdog_dir share existing stale-lock rules; full marker path is recorded in warnings. CLI run/pin forward --watchdog-dir; pin retains warnings in stage2.json.
No EXP-002 analysis performed. Existing unrelated work left untouched.

......................................................
----------------------------------------------------------------------
Ran 54 tests in 1.018s

OK
