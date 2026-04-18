from __future__ import annotations
import argparse
import sys
from csv_warden.column_normalizer import normalize_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "normalize-col",
        help="Normalize string values in specified columns (snake_case, title_case, lower, upper).",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of columns to normalize",
    )
    p.add_argument(
        "--mode",
        default="snake_case",
        choices=["snake_case", "title_case", "lower", "upper"],
        help="Normalization mode (default: snake_case)",
    )
    p.set_defaults(func=cmd_normalize_col)


def cmd_normalize_col(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.columns.split(",") if c.strip()]
    if not columns:
        print("Error: --columns must specify at least one column.", file=sys.stderr)
        sys.exit(1)

    result = normalize_csv(
        input_path=args.input,
        output_path=args.output,
        columns=columns,
        mode=args.mode,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
