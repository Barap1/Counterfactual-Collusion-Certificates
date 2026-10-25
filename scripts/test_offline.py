"""Guarded offline suite entrypoint; a real __main__ file supports spawn workers."""
import os
from pathlib import Path
import runpy
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0, str(root))
    os.environ.setdefault("CCC_STARTER_ROOT", str(root / "starter/collusion_hackathon"))
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    # Install the release scope even when invoked without a PYTHONPATH hook.
    runpy.run_path(str(root / "scripts/offline_guard/sitecustomize.py"))
    from tests.replay.offline_runner import guard
    sys.addaudithook(guard)
    import pytest
    return pytest.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
