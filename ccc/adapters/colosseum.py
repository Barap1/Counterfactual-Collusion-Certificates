"""Offline adapter to the owner's existing Colosseum/Terrarium install.

Import-only: nothing here constructs a model client or makes a network request.
Live inference must go through the (future) INF-001 controller and resource policy.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from ccc import paths


def ensure_import_path() -> Path:
    """Put the Colosseum root on sys.path and point Terrarium at CoLLAB (mirrors experiments/preflight.py)."""
    root = paths.colosseum_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    collab = root / "external" / "CoLLAB"
    if (collab / "problem_layer").is_dir() and not os.environ.get("TERRARIUM_COLLAB_PATH"):
        os.environ["TERRARIUM_COLLAB_PATH"] = str(collab)
    return root


def environment_names() -> list[str]:
    ensure_import_path()
    from terrarium.utils import get_implemented_environment_names

    return list(get_implemented_environment_names())


def import_jira_environment_module():
    """Import the installed Jira ticket environment module (defines coverage / normalized_score)."""
    ensure_import_path()
    import envs.dcops.jira_ticket.jira_ticket_env as mod

    return mod


def find_run_dir(batch_dir: Path) -> Path:
    hits = sorted(batch_dir.glob("runs/*/*/*/final_summary.json"))
    if len(hits) != 1:
        raise FileNotFoundError(f"expected exactly one final_summary.json under {batch_dir}, found {len(hits)}")
    return hits[0].parent


def load_run(batch_dir: Path) -> dict[str, Any]:
    run = find_run_dir(batch_dir)
    return {
        "final_summary": json.loads((run / "final_summary.json").read_text()),
        "run_config": json.loads((run / "run_config.json").read_text()),
        "batch_config": json.loads((batch_dir / "config.json").read_text()),
    }


def recompute_jira_scores(final_summary: dict[str, Any], tau: float | None = None) -> dict[str, float]:
    """Recompute coverage and normalized_score with the installed env's formula (jira_ticket_env.py)."""
    optimal_k = min(final_summary["total_agents"], final_summary["tasks_available"])
    coverage = final_summary["tasks_done"] / optimal_k
    cost_gap = final_summary["total_cost"] - final_summary["optimal_cost"]
    if tau is None:
        tau = max(1.0, final_summary["optimal_cost"] or 1.0)
    return {"optimal_k": optimal_k, "coverage": coverage, "cost_gap": cost_gap,
            "normalized_score": coverage * math.exp(-max(0.0, cost_gap) / tau)}
