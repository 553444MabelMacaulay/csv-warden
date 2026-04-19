"""CLI sub-command: tokenize-col — add token count columns from a text column."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_tokenizer import tokenize_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "tokenize-col",
        help="Append token_count and unique_token_count columns from a text column.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Text column to tokenize")
    p.add_argument("--count-col", default="token_count", help="Name for token count column")
    p.add_argument("--unique-col", default="unique_token_count", help="Name for unique token count column")
    p.add_argument("--encoding", default="utf-8", help="File encoding (default: utf-8)")
    p.set_defaults(func=cmd_tokenize_col)


def cmd_tokenize_col(args: argparse.Namespace) -> None:
    result = tokenize_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        count_col=args.count_col,
        unique_col=args.unique_col,
        encoding=args.encoding,
    )
    print(summary(result))
    if result.errors:
        sys.exit(1)
