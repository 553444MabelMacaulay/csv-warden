"""CLI entry-point for csv-warden."""
from __future__ import annotations

import argparse
import sys

from csv_warden.validator import validate_csv, summary as val_summary
from csv_warden.profiler import profile_csv, summary as prof_summary
from csv_warden.sanitizer import sanitize_csv, summary as san_summary
from csv_warden.deduplicator import deduplicate_csv, summary as dedup_summary
from csv_warden.merger import merge_csv, summary as merge_summary
from csv_warden.transformer import transform_csv, summary as trans_summary
from csv_warden.filter import filter_csv, summary as filt_summary
from csv_warden.sorter import sort_csv, summary as sort_summary
from csv_warden.aggregator import aggregate_csv, summary as agg_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-warden",
        description="Validate, profile, and sanitize CSV files.",
    )
    sub = parser.add_subparsers(dest="command")

    # validate
    p_val = sub.add_parser("validate", help="Validate a CSV file.")
    p_val.add_argument("file")
    p_val.add_argument("--max-rows", type=int, default=None)

    # profile
    p_prof = sub.add_parser("profile", help="Profile a CSV file.")
    p_prof.add_argument("file")

    # sanitize
    p_san = sub.add_parser("sanitize", help="Sanitize a CSV file.")
    p_san.add_argument("file")
    p_san.add_argument("--output", default=None)
    p_san.add_argument("--keep-empty-rows", action="store_true")

    # deduplicate
    p_dedup = sub.add_parser("deduplicate", help="Remove duplicate rows.")
    p_dedup.add_argument("file")
    p_dedup.add_argument("--output", default=None)
    p_dedup.add_argument("--subset", nargs="+", default=None)

    # merge
    p_merge = sub.add_parser("merge", help="Merge multiple CSV files.")
    p_merge.add_argument("files", nargs="+")
    p_merge.add_argument("--output", required=True)

    # transform
    p_trans = sub.add_parser("transform", help="Transform CSV column values.")
    p_trans.add_argument("file")
    p_trans.add_argument("--output", default=None)
    p_trans.add_argument("--transform", required=True)
    p_trans.add_argument("--columns", nargs="+", default=None)

    # filter
    p_filt = sub.add_parser("filter", help="Filter CSV rows.")
    p_filt.add_argument("file")
    p_filt.add_argument("--column", required=True)
    p_filt.add_argument("--value", required=True)
    p_filt.add_argument("--output", default=None)
    p_filt.add_argument("--exclude", action="store_true")

    # sort
    p_sort = sub.add_parser("sort", help="Sort CSV rows.")
    p_sort.add_argument("file")
    p_sort.add_argument("--column", required=True)
    p_sort.add_argument("--output", default=None)
    p_sort.add_argument("--descending", action="store_true")

    # aggregate
    p_agg = sub.add_parser("aggregate", help="Aggregate a numeric CSV column.")
    p_agg.add_argument("file")
    p_agg.add_argument("column", help="Column name to aggregate.")
    p_agg.add_argument("func", help="Aggregation function: sum, mean, min, max, count.")

    return parser


def _exit_with_result(errors: list, output: str) -> None:
    print(output)
    sys.exit(1 if errors else 0)


def main(args=None) -> None:
    parser = build_parser()
    ns = parser.parse_args(args)

    if ns.command == "validate":
        r = validate_csv(ns.file, max_rows=ns.max_rows)
        _exit_with_result(r.errors, val_summary(r))
    elif ns.command == "profile":
        r = profile_csv(ns.file)
        _exit_with_result(r.errors, prof_summary(r))
    elif ns.command == "sanitize":
        r = sanitize_csv(ns.file, output_path=ns.output, drop_empty_rows=not ns.keep_empty_rows)
        _exit_with_result(r.errors, san_summary(r))
    elif ns.command == "deduplicate":
        r = deduplicate_csv(ns.file, output_path=ns.output, subset=ns.subset)
        _exit_with_result(r.errors, dedup_summary(r))
    elif ns.command == "merge":
        r = merge_csv(ns.files, output_path=ns.output)
        _exit_with_result(r.errors, merge_summary(r))
    elif ns.command == "transform":
        r = transform_csv(ns.file, output_path=ns.output, transform=ns.transform, columns=ns.columns)
        _exit_with_result(r.errors, trans_summary(r))
    elif ns.command == "filter":
        r = filter_csv(ns.file, column=ns.column, value=ns.value, output_path=ns.output, exclude=ns.exclude)
        _exit_with_result(r.errors, filt_summary(r))
    elif ns.command == "sort":
        r = sort_csv(ns.file, column=ns.column, output_path=ns.output, descending=ns.descending)
        _exit_with_result(r.errors, sort_summary(r))
    elif ns.command == "aggregate":
        r = aggregate_csv(ns.file, ns.column, ns.func)
        _exit_with_result(r.errors, agg_summary(r))
    else:
        parser.print_help()
        sys.exit(0)
