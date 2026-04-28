"""CLI sub-command: concatenate-col — join multiple columns into one."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_concatenator import concatenate_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "concatenate-col",
        help="Concatenate multiple columns into a single new column.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--cols",
        required=True,
        help="Comma-separated list of columns to concatenate (e.g. first,last)",
    )
    p.add_argument(
        "--new-col",
        default="concatenated",
        dest="new_col",
        help="Name for the new concatenated column (default: concatenated)",
    )
    p.add_argument(
        "--sep",
        default=" ",
        help="Separator string between values (default: single space)",
    )
    p.add_argument(
        "--drop-sources",
        action="store_true",
        default=False,
        help="Remove the source columns from the output",
    )
    p.set_defaults(func=cmd_concatenate_col)


def cmd_concatenate_col(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.cols.split(",") if c.strip()]
    if not columns:
        print("Error: --cols must specify at least one column.", file=sys.stderr)
        sys.exit(1)

    result = concatenate_csv(
        input_path=args.input,
        output_path=args.output,
        columns=columns,
        new_column=args.new_col,
        separator=args.sep,
        drop_sources=args.drop_sources,
    )
    print(summary(result))
    if not result.success:
        sys.exit(1)
