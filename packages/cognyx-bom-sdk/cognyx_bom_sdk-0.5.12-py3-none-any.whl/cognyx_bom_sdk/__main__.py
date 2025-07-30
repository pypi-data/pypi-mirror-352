"""Main entry point for the cognyx-bom-sdk package when run as a module."""

import sys


def main() -> int:
    """Main entry point for the package when run as a module.

    Returns:
        Exit code
    """
    print("cognyx-bom-sdk - Cognyx BOM SDK")
    print("This package is meant to be imported, not executed directly.")
    print("For usage information, please refer to the documentation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
