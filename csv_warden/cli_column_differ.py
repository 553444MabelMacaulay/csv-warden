"""CLI sub-command: differ-col — compare two columns row-by-row."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_differ import diff_columns, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "differ-col",
        help="Compare two columns row-by-row and write a diff column.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("--col-a", required=True, help="First column name.")
    p.add_argument("--col-b", required=True, help="Second column name.")
    p.add_argument("--output", required=True, help="Output CSV file.")
    p.add_argument(
        "--diff-col",
        default="__diff__",
        help="Name for the generated diff column (default: __diff__).",
    )
    p.add_argument(
        "--mode",
        choices=["flag", "delta"],
        default="flag",
        help="'flag' writes True/False; 'delta' writes numeric difference.",
    )
    p.set_defaults(func=cmd_differ_col)


def cmd_differ_col(args: argparse.Namespace) -> None:
    result = diff_columns(
        input_path=args.input,
        col_a=args.col_a,
        col_b=args.col_b,
        output_path=args.output,
        diff_col=args.diff_col,
        mode=args.mode,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
