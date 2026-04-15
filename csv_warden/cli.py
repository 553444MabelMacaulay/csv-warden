"""CLI entry-point for csv-warden."""

from __future__ import annotations

import sys
import argparse
from typing import List

from csv_warden.validator import validate_csv, summary as val_summary
from csv_warden.profiler import profile_csv, summary as prof_summary
from csv_warden.sanitizer import sanitize_csv, summary as san_summary
from csv_warden.deduplicator import deduplicate_csv, summary as ded_summary
from csv_warden.merger import merge_csv, summary as mer_summary
from csv_warden.transformer import transform_csv, summary as tra_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-warden",
        description="Validate, profile, and sanitize CSV files.",
    )
    sub = parser.add_subparsers(dest="command")

    # validate
    p_val = sub.add_parser("validate", help="Validate a CSV file.")
    p_val.add_argument("input", help="Path to CSV file.")

    # profile
    p_pro = sub.add_parser("profile", help="Profile a CSV file.")
    p_pro.add_argument("input", help="Path to CSV file.")

    # sanitize
    p_san = sub.add_parser("sanitize", help="Sanitize a CSV file.")
    p_san.add_argument("input")
    p_san.add_argument("output")
    p_san.add_argument("--keep-empty-rows", action="store_true",
                       default=False)

    # deduplicate
    p_ded = sub.add_parser("deduplicate", help="Remove duplicate rows.")
    p_ded.add_argument("input")
    p_ded.add_argument("output")
    p_ded.add_argument("--subset", nargs="+", default=None)

    # merge
    p_mer = sub.add_parser("merge", help="Merge multiple CSV files.")
    p_mer.add_argument("inputs", nargs="+")
    p_mer.add_argument("--output", required=True)

    # transform
    p_tra = sub.add_parser("transform", help="Transform columns in a CSV.")
    p_tra.add_argument("input")
    p_tra.add_argument("output")
    p_tra.add_argument(
        "--col",
        dest="cols",
        action="append",
        default=[],
        metavar="COLUMN=TRANSFORM",
        help="Column transform pair, e.g. name=upper. Repeatable.",
    )

    return parser


def _exit_with_result(summary_text: str, has_errors: bool) -> None:
    """Print a command result summary and exit with an appropriate code.

    Exits with code 0 when there are no errors, or code 1 otherwise.
    """
    print(summary_text)
    sys.exit(1 if has_errors else 0)


def main(args: List[str] | None = None) -> None:  # noqa: UP007
    """Parse CLI arguments and dispatch to the appropriate sub-command."""
    parser = build_parser()
    ns = parser.parse_args(args)

    if ns.command is None:
        parser.print_help()
        sys.exit(1)

    if ns.command == "validate":
        result = validate_csv(ns.input)
        _exit_with_result(val_summary(result), bool(result.errors))

    elif ns.command == "profile":
        result = profile_csv(ns.input)
        _exit_with_result(prof_summary(result), bool(result.errors))

    elif ns.command == "sanitize":
        result = sanitize_csv(ns.input, ns.output,
                              drop_empty_rows=not ns.keep_empty_rows)
        _exit_with_result(san_summary(result), bool(result.errors))

    elif ns.command == "deduplicate":
        result = deduplicate_csv(ns.input, ns.output, subset=ns.subset)
        _exit_with_result(ded_summary(result), bool(result.errors))

    elif ns.command == "merge":
        result = merge_csv(ns.inputs, ns.output)
        _exit_with_result(mer_summary(result), bool(result.errors))

    elif ns.command == "transform":
        cols = dict(pair.split("=", 1) for pair in ns.cols)
        result = transform_csv(ns.input, ns.output, cols)
        _exit_with_result(tra_summary(result), bool(result.errors))
