"""Recheck inherited DEV counts only, under the offline runner's audit guard."""
import os
from pathlib import Path
import sys
from tests.replay.offline_runner import guard

ROOT = Path.cwd()
os.environ["CCC_STARTER_ROOT"] = str(ROOT / "starter/collusion_hackathon")
sys.addaudithook(guard)

from ccc.audit.placebo_census import main

if __name__ == "__main__":
    for version in (sys.argv[1:] or ["fx1", "fx2"]):
        args = ["--out", str(ROOT / "ops/reports/AMD-IMP-A-evidence" / f"census_{version}.json")]
        if version == "fx1":
            args.append("--fx1")
        main(args)
