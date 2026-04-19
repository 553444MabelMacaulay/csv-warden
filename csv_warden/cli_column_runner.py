"""CLI registration for the run-column command."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_runner import run_column, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "run-col",
        help="Apply a shell command to each value in a column.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to process")
    p.add_argument(
        "--cmd",
        required=True,
        help="Shell command template; use {value} as placeholder",
    )
    p.add_argument(
        "--new-column",
        default=None,
        help="Write result to a new column instead of overwriting",
    )
    p.set_defaults(func=cmd_run_col)


def cmd_run_col(args: argparse.Namespace) -> None:
    result = run_column(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        cmd_template=args.cmd,
        new_column=args.new_column,
    )
    print(summary(result))
    if result.errors and result.rows_processed == 0:
        sys.exit(1)
