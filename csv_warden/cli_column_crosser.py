"""CLI sub-command: cross-tab two categorical columns."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_crosser import cross_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "cross",
        help="Build a cross-tabulation (contingency table) from two columns.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--row-col", required=True, help="Column whose values become row labels")
    p.add_argument("--col-col", required=True, help="Column whose values become column headers")
    p.add_argument("--output", required=True, help="Output CSV file for the cross-tab table")
    p.set_defaults(func=cmd_cross)


def cmd_cross(args: argparse.Namespace) -> None:
    result = cross_csv(
        input_file=args.input,
        row_col=args.row_col,
        col_col=args.col_col,
        output_file=args.output,
    )
    print(summary(result))
    if result.error:
        sys.exit(1)
