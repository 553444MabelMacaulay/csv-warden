"""CLI registration for the infer-types command."""
from __future__ import annotations

import argparse
import sys

from csv_warden.column_typer import infer_types, summary


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "infer-types",
        help="Infer the likely data type of each column.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument(
        "--sample",
        type=int,
        default=100,
        metavar="N",
        help="Number of rows to sample (default: 100).",
    )
    p.set_defaults(func=cmd_infer_types)


def cmd_infer_types(args: argparse.Namespace) -> None:
    """Run the infer-types command.

    Exits with code 1 if any type inference errors are encountered,
    or with code 2 if the input file cannot be read.
    """
    try:
        result = infer_types(args.input, sample_size=args.sample)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: could not read file: {exc}", file=sys.stderr)
        sys.exit(2)
    print(summary(result))
    if result.errors:
        sys.exit(1)
