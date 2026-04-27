"""CLI registration for the column-truncate command."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_truncator import truncate_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "truncate-col",
        help="Truncate string values in a column to a maximum character length.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to truncate")
    p.add_argument(
        "--max-length",
        required=True,
        type=int,
        dest="max_length",
        help="Maximum number of characters to keep",
    )
    p.add_argument(
        "--suffix",
        default="",
        help="Optional suffix to append when a value is truncated (e.g. '...')",
    )
    p.set_defaults(func=cmd_truncate_col)


def cmd_truncate_col(args: argparse.Namespace) -> None:
    result = truncate_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        max_length=args.max_length,
        suffix=args.suffix,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
