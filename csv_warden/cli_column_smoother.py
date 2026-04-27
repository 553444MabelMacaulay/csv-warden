"""CLI registration for the column-smoother command."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_smoother import smooth_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "smooth-col",
        help="Apply moving-average smoothing to a numeric column.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument("--column", required=True, help="Column to smooth.")
    p.add_argument(
        "--window",
        type=int,
        default=3,
        help="Half-window size (full window = 2*window+1). Default: 3.",
    )
    p.add_argument(
        "--method",
        choices=["mean", "gaussian"],
        default="mean",
        help="Smoothing method. Default: mean.",
    )
    p.set_defaults(func=cmd_smooth_col)


def cmd_smooth_col(args: argparse.Namespace) -> None:
    result = smooth_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        window=args.window,
        method=args.method,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
