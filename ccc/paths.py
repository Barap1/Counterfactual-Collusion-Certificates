"""Resolve local, gitignored locations (starter checkout, archived pilot) without hardcoding secrets."""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_MANIFEST = REPO_ROOT / "ops" / "environment.local.json"


def _local_manifest() -> dict:
    try:
        return json.loads(LOCAL_MANIFEST.read_text())
    except (OSError, ValueError):
        return {}


def starter_root() -> Path:
    env = os.environ.get("CCC_STARTER_ROOT")
    if env:
        return Path(env)
    manifest = _local_manifest().get("paths", {}).get("starter_root")
    return Path(manifest) if manifest else REPO_ROOT / "starter" / "collusion_hackathon"


def colosseum_root() -> Path:
    return starter_root() / "colosseum"


def pilot_archive_root() -> Path:
    return REPO_ROOT / "results" / "baselines"
