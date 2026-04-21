"""CLI sub-command: interpolate-col"""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_interpolator import interpolate_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "interpolate-col",
        help="Fill numeric gaps in a column via linear or forward interpolation.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to interpolate")
    p.add_argument(
        "--method",
        choices=["linear", "forward"],
        default="linear",
        help="Interpolation method (default: linear)",
    )
    p.set_defaults(func=cmd_interpolate_col)


def cmd_interpolate_col(args: argparse.Namespace) -> None:
    result = interpolate_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        method=args.method,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
