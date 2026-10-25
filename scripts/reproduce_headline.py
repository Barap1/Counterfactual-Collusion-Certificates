#!/usr/bin/env python3
"""Small, stdlib-only judge entrypoint. Checks archive SHA before safe extraction.

Runs only the independent raw arithmetic, never the experimental runner.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    archive = ROOT / "docs/runner/archives/exp002-live.tar.gz"
    expected = archive.with_suffix(archive.suffix + ".sha256").read_text().split()[0]
    with archive.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise SystemExit("EXP-002 archive SHA-256 mismatch; refusing extraction")
    with tempfile.TemporaryDirectory(prefix="ccc-headline-") as directory:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(directory, filter="data")
        result = subprocess.run([sys.executable, "-I", str(ROOT / "review/reproduce_headline/independent.py"),
                                 "--input", str(Path(directory) / "exp002-live")],
                                check=True, text=True, capture_output=True)
        data = json.loads(result.stdout)
        reference = json.loads((ROOT / "review/reproduce_headline/exp002_independent.json").read_text())
        for field in ("Delta", "sign_flip", "pairs"):
            if data[field] != reference[field]:
                raise SystemExit("Independent arithmetic differs: " + field)
        print(json.dumps({"archive_sha256": actual, "Delta": data["Delta"],
                          "sign_flip": data["sign_flip"], "pairs": data["pairs"],
                          "status": "EXECUTED: matches frozen independent arithmetic; directional hypothesis NOT supported"}, indent=2))


if __name__ == "__main__":
    main()
