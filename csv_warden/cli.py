"""CLI entry point for csv-warden."""

import sys
import argparse

from csv_warden import __version__
from csv_warden.validator import validate_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-warden",
        description="Validate, profile, and sanitize CSV files before pipeline ingestion.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate", help="Validate a CSV file.")
    validate_cmd.add_argument("file", help="Path to the CSV file.")
    validate_cmd.add_argument(
        "--delimiter", default=",", help="Field delimiter (default: comma)."
    )
    validate_cmd.add_argument(
        "--expected-columns", type=int, default=None, help="Expected number of columns."
    )
    validate_cmd.add_argument(
        "--require-headers",
        nargs="+",
        metavar="HEADER",
        default=None,
        help="One or more header names that must be present.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_csv(
            filepath=args.file,
            delimiter=args.delimiter,
            expected_columns=args.expected_columns,
            required_headers=args.require_headers,
        )
        print(result.summary())
        return 0 if result.is_valid else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
