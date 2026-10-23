"""python -m ccc.runner plan|run|status --help"""
import argparse
import json
import sys

from .manifest import load, plan


def main(argv=None):
    parser = argparse.ArgumentParser(description="Immutable Gate B collection")
    commands = parser.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan")
    planning.add_argument("manifest")
    execution = commands.add_parser("run")
    execution.add_argument("manifest")
    execution.add_argument("--output", required=True)
    mode = execution.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    execution.add_argument("--retry-failed", action="store_true")
    inspection = commands.add_parser("status")
    inspection.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            result = plan(load(args.manifest))
        else:
            from .collector import run, status
            result = status(args.output) if args.command == "status" else run(
                load(args.manifest), args.output, dry_run=args.dry_run, live=args.live, retry_failed=args.retry_failed)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"runner refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
