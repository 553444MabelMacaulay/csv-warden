"""CLI sub-command: format-col"""
from __future__ import annotations

import sys
import argparse
from csv_warden.column_formatter import format_csv, summary, SUPPORTED_FORMATS


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "format-col",
        help="Apply string formatting (upper/lower/title/strip/capitalize) to columns.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--fmt",
        metavar="COL:FORMAT",
        action="append",
        required=True,
        help=(
            f"Column and format, e.g. name:upper. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}. Repeatable."
        ),
    )
    p.set_defaults(func=cmd_format_col)


def cmd_format_col(args: argparse.Namespace) -> None:
    column_formats: dict[str, str] = {}
    for item in args.fmt:
        if ":" not in item:
            print(f"ERROR: invalid --fmt value '{item}', expected COL:FORMAT", file=sys.stderr)
            sys.exit(1)
        col, fmt = item.split(":", 1)
        column_formats[col.strip()] = fmt.strip()

    result = format_csv(args.input, args.output, column_formats)
    print(summary(result))
    if result.errors:
        sys.exit(1)
