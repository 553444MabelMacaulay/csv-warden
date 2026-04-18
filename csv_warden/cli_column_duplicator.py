"""CLI sub-command: duplicate-col."""
from __future__ import annotations
import sys
from csv_warden.column_duplicator import duplicate_columns, summary


def register(subparsers):
    p = subparsers.add_parser(
        "duplicate-col",
        help="Duplicate one or more columns under new names.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("output", help="Output CSV file.")
    p.add_argument(
        "--map",
        dest="mappings",
        metavar="SRC:DST",
        action="append",
        required=True,
        help="Column mapping as SRC:DST. Repeatable.",
    )
    p.set_defaults(func=cmd_duplicate_col)


def cmd_duplicate_col(args):
    mapping = {}
    for m in args.mappings:
        if ":" not in m:
            print(f"Invalid mapping '{m}'. Expected SRC:DST.", file=sys.stderr)
            sys.exit(1)
        src, dst = m.split(":", 1)
        mapping[src.strip()] = dst.strip()

    result = duplicate_columns(args.input, args.output, mapping)
    print(summary(result))
    if result.errors:
        sys.exit(1)
