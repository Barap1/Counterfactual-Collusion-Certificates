"""Shared helpers for replay tests: socket guard (any connect attempt fails the run) and pilot paths."""

from __future__ import annotations

import socket
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PILOT_BATCH = REPO / "results" / "baselines" / "colosseum_positive_control_seed1" / "20261023-111625"

_real_connect = socket.socket.connect
attempts: list = []


def _guard(self, address, *a, **k):  # pragma: no cover - only on a violation
    attempts.append(address)
    raise OSError(f"network disabled in offline tests: {address!r}")


def block_network():
    socket.socket.connect = _guard


def restore_network():
    socket.socket.connect = _real_connect


def pilot_run_dir() -> Path:
    hits = sorted(PILOT_BATCH.glob("runs/*/*/*/final_summary.json"))
    return hits[0].parent if len(hits) == 1 else None
