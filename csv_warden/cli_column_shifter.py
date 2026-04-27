"""CLI sub-command: shift-col  – shift numeric column values."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_shifter import shift_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "shift-col",
        help="Shift numeric column values by offset and/or scale factor.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument("--column", required=True, help="Column to shift.")
    p.add_argument(
        "--offset",
        type=float,
        default=0.0,
        help="Constant to add after scaling (default 0).",
    )
    p.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Multiply values by this factor before adding offset (default 1).",
    )
    p.add_argument(
        "--suffix",
        default=None,
        help="If set, write results to a new column '<column><suffix>' instead of overwriting.",
    )
    p.set_defaults(func=cmd_shift_col)


def cmd_shift_col(args: argparse.Namespace) -> None:
    result = shift_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        offset=args.offset,
        scale=args.scale,
        suffix=args.suffix,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
