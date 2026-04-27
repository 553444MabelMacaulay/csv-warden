"""CLI sub-command: regex-extract  — extract named groups from a column."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_regex_extractor import regex_extract_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "regex-extract",
        help="Extract named regex capture groups from a column into new columns",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Source column to apply regex to")
    p.add_argument(
        "--pattern",
        required=True,
        help="Regex with named groups, e.g. '(?P<year>\\d{4})-(?P<month>\\d{2})'",
    )
    p.add_argument(
        "--drop-original",
        action="store_true",
        default=False,
        help="Drop the source column from the output",
    )
    p.add_argument(
        "--fill-value",
        default="",
        help="Value to use when the pattern does not match (default: empty string)",
    )
    p.set_defaults(func=cmd_regex_extract)


def cmd_regex_extract(args: argparse.Namespace) -> None:
    result = regex_extract_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        pattern=args.pattern,
        drop_original=args.drop_original,
        fill_value=args.fill_value,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
