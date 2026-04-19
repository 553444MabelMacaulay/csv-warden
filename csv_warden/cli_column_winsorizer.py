"""CLI registration for the winsorize-col command."""
from __future__ import annotations
import argparse
import sys
from csv_warden.column_winsorizer import winsorize_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "winsorize-col",
        help="Cap numeric column values at percentile bounds.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of columns to winsorize.",
    )
    p.add_argument(
        "--lower",
        type=float,
        default=5.0,
        help="Lower percentile bound (default: 5).",
    )
    p.add_argument(
        "--upper",
        type=float,
        default=95.0,
        help="Upper percentile bound (default: 95).",
    )
    p.set_defaults(func=cmd_winsorize_col)


def cmd_winsorize_col(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.columns.split(",") if c.strip()]
    if not columns:
        print("Error: --columns must specify at least one column.", file=sys.stderr)
        sys.exit(1)

    result = winsorize_csv(
        args.input,
        args.output,
        columns,
        lower_pct=args.lower,
        upper_pct=args.upper,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
