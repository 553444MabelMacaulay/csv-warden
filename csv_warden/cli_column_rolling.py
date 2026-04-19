from __future__ import annotations
import argparse
import sys
from csv_warden.column_rolling import rolling_csv, summary


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rolling-col",
        help="Compute a rolling window statistic for a numeric column.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to compute rolling stat on")
    p.add_argument("--window", type=int, required=True, help="Window size")
    p.add_argument(
        "--func",
        default="mean",
        choices=["mean", "sum", "min", "max"],
        help="Aggregation function (default: mean)",
    )
    p.add_argument("--new-column", default=None, help="Name for the new column")
    p.set_defaults(func_handler=cmd_rolling_col)


def cmd_rolling_col(args: argparse.Namespace) -> int:
    result = rolling_csv(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        window=args.window,
        func=args.func,
        new_column=args.new_column,
    )
    print(summary(result))
    if result.errors:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register(subs)
    args = parser.parse_args()
    sys.exit(args.func_handler(args))
