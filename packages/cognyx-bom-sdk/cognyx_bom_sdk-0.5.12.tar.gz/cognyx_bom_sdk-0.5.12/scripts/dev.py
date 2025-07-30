#!/usr/bin/env python
"""Development helper script for cognyx-bom-sdk."""

import argparse
import subprocess
import sys


def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def lint() -> bool:
    """Run linting."""
    return run_command(["uv", "pip", "run", "ruff", "check", "."])


def format_code() -> bool:
    """Run code formatting."""
    return run_command(["uv", "pip", "run", "ruff", "format", "."])


def typecheck() -> bool:
    """Run type checking."""
    return run_command(["uv", "pip", "run", "mypy", "src"])


def test(args: argparse.Namespace) -> bool:
    """Run tests."""
    cmd = ["uv", "pip", "run", "pytest"]
    if args.coverage:
        cmd.extend(["--cov=cognyx_bom_sdk", "--cov-report=term-missing"])
    if args.verbose:
        cmd.append("-v")
    return run_command(cmd)


def coverage(args: argparse.Namespace) -> bool:
    """Run test coverage and generate reports."""
    cmd = ["uv", "pip", "run", "pytest"]
    coverage_options = ["--cov=cognyx_bom_sdk"]

    # Add coverage reports based on args
    reports = []
    if args.html:
        reports.append("html")
    if args.xml:
        reports.append("xml")
    if args.annotate:
        reports.append("annotate")

    # Always include term-missing for console output
    reports.append("term-missing")

    for report in reports:
        coverage_options.append(f"--cov-report={report}")

    cmd.extend(coverage_options)

    if args.verbose:
        cmd.append("-v")

    if args.fail_under is not None:
        cmd.append(f"--cov-fail-under={args.fail_under}")

    success = run_command(cmd)

    if success and args.html:
        print("\nHTML coverage report generated in htmlcov/index.html")

    return success


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development helper for cognyx-bom-sdk")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Lint command
    subparsers.add_parser("lint", help="Run linting")

    # Format command
    subparsers.add_parser("format", help="Run code formatting")

    # Typecheck command
    subparsers.add_parser("typecheck", help="Run type checking")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Coverage command
    coverage_parser = subparsers.add_parser(
        "coverage", help="Run test coverage and generate reports"
    )
    coverage_parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    coverage_parser.add_argument("--xml", action="store_true", help="Generate XML coverage report")
    coverage_parser.add_argument(
        "--annotate", action="store_true", help="Annotate source files with coverage"
    )
    coverage_parser.add_argument(
        "--fail-under", type=float, help="Fail if coverage percentage is under this value"
    )
    coverage_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # All command
    subparsers.add_parser("all", help="Run all checks")

    args = parser.parse_args()

    if args.command == "lint":
        success = lint()
    elif args.command == "format":
        success = format_code()
    elif args.command == "typecheck":
        success = typecheck()
    elif args.command == "test":
        success = test(args)
    elif args.command == "coverage":
        success = coverage(args)
    elif args.command == "all":
        success = (
            format_code()
            and lint()
            and typecheck()
            and test(argparse.Namespace(coverage=True, verbose=False))
        )
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
