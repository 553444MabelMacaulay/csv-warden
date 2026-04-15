"""CLI entry-point for csv-warden."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csv_warden.profiler import profile_csv
from csv_warden.sanitizer import sanitize_csv
from csv_warden.validator import validate_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-warden",
        description="Validate, profile, and sanitize CSV files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- validate ---
    val = sub.add_parser("validate", help="Validate a CSV file.")
    val.add_argument("file", help="Path to the CSV file.")
    val.add_argument(
        "--max-warnings",
        type=int,
        default=None,
        metavar="N",
        help="Treat run as failed if warnings exceed N.",
    )

    # --- profile ---
    prof = sub.add_parser("profile", help="Profile a CSV file.")
    prof.add_argument("file", help="Path to the CSV file.")

    # --- sanitize ---
    san = sub.add_parser("sanitize", help="Sanitize a CSV file.")
    san.add_argument("file", help="Path to the CSV file.")
    san.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="DEST",
        help="Write sanitized output to DEST instead of overwriting source.",
    )
    san.add_argument(
        "--no-strip",
        action="store_true",
        help="Disable whitespace stripping.",
    )
    san.add_argument(
        "--keep-empty-rows",
        action="store_true",
        help="Do not drop fully-empty rows.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        try:
            result = validate_csv(args.file)
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        print(result.summary())
        if result.errors:
            return 1
        if args.max_warnings is not None and len(result.warnings) > args.max_warnings:
            return 1
        return 0

    if args.command == "profile":
        try:
            report = profile_csv(args.file)
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        print(report.summary())
        return 0

    if args.command == "sanitize":
        try:
            result = sanitize_csv(
                args.file,
                dest=args.output,
                strip_whitespace=not args.no_strip,
                drop_empty_rows=not args.keep_empty_rows,
            )
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        print(result.summary())
        return 0

    return 0  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
