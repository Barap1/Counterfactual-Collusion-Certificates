"""Python-level offline fallback when nested macOS sandbox-exec is unavailable.

Usage: python -m ccc.runner.offline unittest discover -s tests/runner -t .
       python -m ccc.runner.offline ccc.runner run ... --dry-run
This is a Python socket audit guard, not an OS sandbox for arbitrary native code.
"""
import runpy
import sys


def deny_network(event, args):
    if event in {"socket.connect", "socket.connect_ex", "socket.sendto", "socket.sendmsg",
                 "socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr"}:
        raise PermissionError("EXP-000 offline verification denies network and DNS")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"unittest", "ccc.runner"}:
        raise SystemExit("expected unittest or ccc.runner module")
    sys.addaudithook(deny_network)
    module = sys.argv.pop(1)
    runpy.run_module(module, run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
