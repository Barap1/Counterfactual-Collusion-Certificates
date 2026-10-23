"""Fallback for hosts denying nested sandbox-exec. Stdlib discovery with hard audit guards.

Usage: python -m tests.replay.offline_runner -s tests/replay -t .
No production modules are patched; the audit hook cannot be removed by suite socket mocks.
"""
import os
from pathlib import Path
import sys
import unittest


def guard(event, args):
    if event in ("socket.connect", "socket.getaddrinfo", "socket.sendto", "socket.sendmsg"):
        raise PermissionError("ENG-003 offline runner: network forbidden")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0])
        if Path(name).name in (".env", "compute.env") or name.endswith(".local.json"):
            raise PermissionError("ENG-003 offline runner: secret file forbidden")


if __name__ == "__main__":
    os.environ["CCC_STARTER_ROOT"] = str(Path(__file__).resolve().parents[2] / "starter/collusion_hackathon")
    sys.addaudithook(guard)
    unittest.main(module=None, argv=[sys.argv[0], "discover", *sys.argv[1:]])
