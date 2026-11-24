# Command line entry point: parses commands and reports those not built yet.
import argparse
import sys

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cut_planner", description="Local cut list planner.")
    parser.add_argument("--version", action="version", version=f"cut_planner {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="{serve,plan}")
    serve = sub.add_parser("serve", help="run the local app (not implemented yet)")
    serve.add_argument("--port", type=int, default=8770)
    serve.add_argument("--data-dir", default="./data")
    plan = sub.add_parser("plan", help="plan a project file (not implemented yet)")
    plan.add_argument("project", metavar="project.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        print("not implemented yet: see #2", file=sys.stderr)
        return 1
    if args.command == "plan":
        print("not implemented yet: see #3", file=sys.stderr)
        return 1
    parser.print_help()
    return 0
