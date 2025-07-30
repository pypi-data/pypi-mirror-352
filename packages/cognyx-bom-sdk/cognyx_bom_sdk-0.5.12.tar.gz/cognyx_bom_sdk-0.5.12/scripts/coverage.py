#!/usr/bin/env python
"""Test coverage script for cognyx-bom-sdk."""

import sys


def main() -> int:
    """Run pytest with coverage options."""
    import pytest

    # Default coverage options
    coverage_args: list[str] = [
        "--cov=cognyx_bom_sdk",
        "--cov-report=term-missing",
    ]

    # Parse command line arguments
    html_report = "--html" in sys.argv
    xml_report = "--xml" in sys.argv
    annotate = "--annotate" in sys.argv

    # Add report formats based on arguments
    if html_report:
        coverage_args.append("--cov-report=html")
    if xml_report:
        coverage_args.append("--cov-report=xml")
    if annotate:
        coverage_args.append("--cov-report=annotate")

    # Check for minimum coverage requirement
    for arg in sys.argv:
        if arg.startswith("--min="):
            try:
                min_value = float(arg.split("=")[1])
                coverage_args.append(f"--cov-fail-under={min_value}")
            except (IndexError, ValueError):
                print(f"Invalid minimum coverage value: {arg}")
                return 1

    # Construct the full argument list
    args = [*coverage_args, "tests"]

    # Print information about the coverage run
    print(f"Running pytest with coverage: {' '.join(args)}")

    # Run pytest with coverage
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
