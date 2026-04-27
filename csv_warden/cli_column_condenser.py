"""CLI sub-command: condense-col — merge columns via a template string."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_condenser import condense_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "condense-col",
        help="Merge multiple columns into one using a template string.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--template",
        required=True,
        help="Template string with column placeholders, e.g. '{first} {last}'",
    )
    p.add_argument(
        "--new-column",
        required=True,
        dest="new_column",
        help="Name for the new condensed column",
    )
    p.add_argument(
        "--drop-sources",
        action="store_true",
        default=False,
        help="Remove the source placeholder columns from the output",
    )
    p.set_defaults(func=cmd_condense_col)


def cmd_condense_col(args: argparse.Namespace) -> int:
    result = condense_csv(
        input_path=args.input,
        output_path=args.output,
        template=args.template,
        new_column=args.new_column,
        drop_sources=args.drop_sources,
    )
    print(summary(result))
    if result.errors and result.rows_processed == 0:
        return 1
    return 0
