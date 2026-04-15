"""CLI entry-point for csv-warden."""

from __future__ import annotations

import argparse
import sys

from csv_warden.validator import validate_csv
from csv_warden.profiler import profile_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-warden",
        description="Validate, profile, and sanitize CSV files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- validate ---
    val_p = sub.add_parser("validate", help="Validate a CSV file.")
    val_p.add_argument("file", help="Path to the CSV file.")
    val_p.add_argument(
        "--required-columns",
        nargs="+",
        metavar="COL",
        default=[],
        help="Column names that must be present.",
    )
    val_p.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Warn if row count exceeds this limit.",
    )

    # --- profile ---
    prof_p = sub.add_parser("profile", help="Profile a CSV file.")
    prof_p.add_argument("file", help="Path to the CSV file.")
    prof_p.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top values to show per column (default: 5).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_csv(
            args.file,
            required_columns=args.required_columns,
            max_rows=args.max_rows,
        )
        print(result.summary())
        return 0 if result.valid else 1

    if args.command == "profile":
        try:
            report = profile_csv(args.file, top_n=args.top_n)
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(report.summary())
        return 0

    return 0  # unreachable but satisfies type checkers


if __name__ == "__main__":
    sys.exit(main())
