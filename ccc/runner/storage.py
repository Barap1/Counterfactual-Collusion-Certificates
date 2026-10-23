"""Exclusive, fsynced, hash-enveloped evidence; flock prevents concurrent collectors."""
import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path

from .manifest import ROOT, canonical, digest, file_hash


def output_root(path):
    path = Path(path).resolve()
    # EXP-000 owns this evidence subtree. Never write archived results or other workers' paths.
    if not path.is_relative_to(ROOT / "docs" / "runner"):
        raise ValueError("collection output must be under docs/runner/")
    return path


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical({"sha256": digest(data), "data": data}) + b"\n"
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return digest(data)


def get(path):
    record = json.loads(Path(path).read_text())
    if record["sha256"] != digest(record["data"]):
        raise ValueError(f"evidence hash mismatch: {path}")
    return record["data"]


@contextmanager
def lock(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".collector.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another collector holds this output root") from exc
        try:
            yield
        finally:
            # Keep the inode: unlinking permits a second collector to bypass waiters.
            fcntl.flock(stream, fcntl.LOCK_UN)


def verify(root):
    paths = sorted(Path(root).rglob("*.json"))
    for path in paths:
        # Watchdog sidecars are raw JSON, outside the collector envelope contract.
        if path.parent == Path(root) and path.name in ("WATCHDOG_EXIT.json", "WATCHDOG_STOP.json"):
            json.loads(path.read_text())
            continue
        if "replay_ledger" not in path.relative_to(root).parts:
            get(path)
    for events in Path(root).rglob("replay_ledger/*/events.jsonl"):
        from ccc.replay.ledger import verify_branch
        verify_branch(events)
    for seal in Path(root).rglob("seal.json"):
        for rel, expected in get(seal).items():
            target = (seal.parent / rel).resolve()
            if not target.is_relative_to(seal.parent.resolve()) or file_hash(target) != expected:
                raise ValueError(f"sealed artifact missing or changed: {target}")
    return len(paths)


def seal(root):
    put(Path(root) / "seal.json", {str(p.relative_to(root)): file_hash(p)
                                   for p in sorted(Path(root).rglob("*")) if p.is_file()})
