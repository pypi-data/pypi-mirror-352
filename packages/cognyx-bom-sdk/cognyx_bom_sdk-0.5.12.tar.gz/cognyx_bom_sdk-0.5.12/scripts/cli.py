"""CLI module for cognyx-bom-sdk development."""

import argparse
import subprocess
import sys


def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """Run a command and return its success status.

    Args:
        cmd: Command to run as a list of strings
        cwd: Current working directory

    Returns:
        True if command succeeded, False otherwise
    """
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


def lint(args: list[str] | None = None) -> int:
    """Run linting.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    success = run_command(["ruff", "check", "."])
    return 0 if success else 1


def format_code(args: list[str] | None = None) -> int:
    """Run code formatting.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    success = run_command(["ruff", "format", "."])
    return 0 if success else 1


def typecheck(args: list[str] | None = None) -> int:
    """Run type checking.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    success = run_command(["mypy", "src"])
    return 0 if success else 1


def test(args: list[str] | None = None) -> int:
    """Run tests.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if args is None:
        args = []

    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parsed_args, remaining = parser.parse_known_args(args)

    cmd = ["pytest"]
    if parsed_args.coverage:
        cmd.extend(["--cov=cognyx_bom_sdk", "--cov-report=term-missing"])
    if parsed_args.verbose:
        cmd.append("-v")
    cmd.extend(remaining)

    success = run_command(cmd)
    return 0 if success else 1


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="cognyx-bom-sdk CLI")
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

    args = parser.parse_args()

    if args.command == "lint":
        return lint()
    elif args.command == "format":
        return format_code()
    elif args.command == "typecheck":
        return typecheck()
    elif args.command == "test":
        return test(sys.argv[2:])
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
