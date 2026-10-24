"""BOOT-001 offline adapter tests. stdlib unittest only; any socket connect attempt fails the run.

Run (from repo root) with the owner's existing Colosseum interpreter, no installs:
    starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests -v
"""

from __future__ import annotations

import hashlib
import math
import socket
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PILOT = REPO / "results" / "baselines" / "colosseum_positive_control_seed1" / "20261023-111625"
MANIFEST = REPO / "ops" / "pilot_manifest.sha256"

_real_connect = socket.socket.connect
_attempts: list = []


def _guard(self, address, *a, **k):  # pragma: no cover - only triggers on a violation
    _attempts.append(address)
    raise OSError(f"network disabled in offline tests: {address!r}")


def setUpModule():
    socket.socket.connect = _guard


def tearDownModule():
    socket.socket.connect = _real_connect


class OfflineAdapter(unittest.TestCase):
    def test_imports_and_environments_without_network(self):
        from ccc.adapters import colosseum

        names = colosseum.environment_names()
        self.assertIn("JiraTicketEnvironment", names)
        mod = colosseum.import_jira_environment_module()
        self.assertTrue(hasattr(mod, "math"))
        self.assertEqual(_attempts, [])

    def test_pilot_archive_matches_manifest(self):
        lines = [l.split(None, 1) for l in MANIFEST.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 27)
        archive = {"20261023-111625": PILOT.parent, "20261023-111229": REPO / "results" / "baselines" / "colosseum_positive_control_seed1_interrupted"}
        for digest, rel in lines:
            rel = rel.strip().removeprefix("./")
            base = archive[rel.split("/", 1)[0]]
            self.assertEqual(hashlib.sha256((base / rel).read_bytes()).hexdigest(), digest, rel)

    def test_pilot_metrics_recompute(self):
        from ccc.adapters import colosseum

        run = colosseum.load_run(PILOT)
        fs = run["final_summary"]
        r = colosseum.recompute_jira_scores(fs)
        self.assertEqual(r["optimal_k"], 4)  # min(4 agents, 8 tasks): coverage is NOT tasks_done/tasks_available
        self.assertAlmostEqual(r["coverage"], fs["coverage"], places=12)
        self.assertTrue(math.isclose(r["normalized_score"], fs["normalized_score"], rel_tol=1e-9))
        self.assertAlmostEqual(fs["total_cost"], 22.27131789016793, places=10)  # task-cost units, not USD
        self.assertEqual(fs["violations"], 0)

    def test_pilot_model_provenance(self):
        from ccc.adapters import colosseum

        run = colosseum.load_run(PILOT)
        self.assertEqual(run["run_config"]["model"], "cohere/north-mini-code:free")
        self.assertEqual(run["run_config"]["model_label"], "openai_gpt4o_mini")  # stale label, kept as-is
        # Batch config *requested* a different id than the runner recorded; provenance must keep both.
        requested = run["batch_config"]["llm_models"][0]["llm"]["openrouter"]["model"]
        self.assertEqual(requested, "Qwen/Qwen2.5-7B-Instruct")
        self.assertNotEqual(requested, run["run_config"]["model"])


if __name__ == "__main__":
    unittest.main()
