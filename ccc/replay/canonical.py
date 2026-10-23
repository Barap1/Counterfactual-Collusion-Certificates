"""Canonical serialization and hashing.

Two encodings, on purpose:

* ``state_bytes`` keeps dict insertion order. Upstream code iterates dicts in insertion order
  (e.g. ``JiraTicketEnvironment._evaluate_assignment`` sums costs in ``assignment`` order), so a
  snapshot that re-sorted keys could change float summation order after restore. Snapshots are
  stored and hashed with this encoding.
* ``request_bytes`` sorts keys. It identifies a model request; JSON object key order carries no
  meaning for an HTTP chat-completions payload.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _default(obj: Any) -> Any:
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if isinstance(obj, tuple):
        return list(obj)
    raise TypeError(f"not canonically serializable: {type(obj).__name__}")


def state_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
                      default=_default).encode("utf-8")


def request_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
                      allow_nan=False, default=_default).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def state_sha256(obj: Any) -> str:
    return sha256_bytes(state_bytes(obj))


def request_sha256(obj: Any) -> str:
    return sha256_bytes(request_bytes(obj))


def deep_copy_json(obj: Any) -> Any:
    """Independent copy through JSON (breaks every alias; rejects non-JSON state)."""
    return json.loads(state_bytes(obj))
