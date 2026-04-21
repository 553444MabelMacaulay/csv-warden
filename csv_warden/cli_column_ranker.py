"""CLI sub-command: rank-col — rank values in a numeric CSV column."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_ranker import rank_csv, summary, SUPPORTED_METHODS


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "rank-col",
        help="Rank values in a numeric column (dense / min / percent).",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument("--column", required=True, help="Column to rank.")
    p.add_argument(
        "--method",
        default="dense",
        choices=SUPPORTED_METHODS,
        help="Ranking method (default: dense).",
    )
    p.add_argument(
        "--new-column",
        default=None,
        dest="new_column",
        help="Name for the rank column (default: <column>_rank).",
    )
    p.add_argument(
        "--descending",
        action="store_true",
        help="Rank in descending order (highest value = rank 1).",
    )
    p.set_defaults(func=cmd_rank_col)


def cmd_rank_col(args: argparse.Namespace) -> None:
    result = rank_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        method=args.method,
        new_column=args.new_column,
        ascending=not args.descending,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
