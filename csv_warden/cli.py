"""CLI entry-point for csv-warden."""

from __future__ import annotations

import sys
import click

from csv_warden import validator, profiler, sanitizer, deduplicator, merger
from csv_warden import transformer, filter as csv_filter, sorter, aggregator, renamer
from csv_warden import splitter


@click.group()
def main() -> None:
    """csv-warden: validate, profile, and sanitize CSV files."""


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------
@main.command("validate")
@click.argument("input_file")
def cmd_validate(input_file: str) -> None:
    result = validator.validate_csv(input_file)
    click.echo(validator.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# profile
# ---------------------------------------------------------------------------
@main.command("profile")
@click.argument("input_file")
@click.option("--min-fill-rate", default=0.0, type=float)
def cmd_profile(input_file: str, min_fill_rate: float) -> None:
    result = profiler.profile_csv(input_file)
    if result is None:
        click.echo(f"Error: could not read {input_file}")
        sys.exit(1)
    click.echo(profiler.summary(result))
    low = profiler.columns_below_fill_rate(result, min_fill_rate)
    if low:
        click.echo(f"Columns below fill rate {min_fill_rate}: {low}")
        sys.exit(1)
    sys.exit(0)


# ---------------------------------------------------------------------------
# sanitize
# ---------------------------------------------------------------------------
@main.command("sanitize")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--drop-empty-rows", is_flag=True, default=False)
def cmd_sanitize(input_file: str, output_file: str, drop_empty_rows: bool) -> None:
    result = sanitizer.sanitize_csv(input_file, output_file, drop_empty_rows=drop_empty_rows)
    click.echo(sanitizer.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------
@main.command("deduplicate")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--subset", default=None, help="Comma-separated column names")
def cmd_deduplicate(input_file: str, output_file: str, subset: str | None) -> None:
    cols = [c.strip() for c in subset.split(",")] if subset else None
    result = deduplicator.deduplicate_csv(input_file, output_file, subset=cols)
    click.echo(deduplicator.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------
@main.command("merge")
@click.argument("input_files", nargs=-1, required=True)
@click.option("--output", required=True)
def cmd_merge(input_files: tuple[str, ...], output: str) -> None:
    result = merger.merge_csv(list(input_files), output)
    click.echo(merger.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# transform
# ---------------------------------------------------------------------------
@main.command("transform")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--transform", "transform_name", required=True)
@click.option("--columns", default=None)
def cmd_transform(input_file: str, output_file: str, transform_name: str, columns: str | None) -> None:
    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = transformer.transform_csv(input_file, output_file, transform_name, columns=cols)
    click.echo(transformer.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# filter
# ---------------------------------------------------------------------------
@main.command("filter")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--column", required=True)
@click.option("--value", required=True)
@click.option("--exclude", is_flag=True, default=False)
def cmd_filter(input_file: str, output_file: str, column: str, value: str, exclude: bool) -> None:
    result = csv_filter.filter_csv(input_file, output_file, column=column, value=value, exclude=exclude)
    click.echo(csv_filter.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# sort
# ---------------------------------------------------------------------------
@main.command("sort")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--column", required=True)
@click.option("--descending", is_flag=True, default=False)
def cmd_sort(input_file: str, output_file: str, column: str, descending: bool) -> None:
    result = sorter.sort_csv(input_file, output_file, column=column, descending=descending)
    click.echo(sorter.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------
@main.command("aggregate")
@click.argument("input_file")
@click.option("--column", required=True)
@click.option("--operation", required=True)
def cmd_aggregate(input_file: str, column: str, operation: str) -> None:
    result = aggregator.aggregate_csv(input_file, column=column, operation=operation)
    click.echo(aggregator.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# rename
# ---------------------------------------------------------------------------
@main.command("rename")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--mapping", required=True, help="old:new,old2:new2")
def cmd_rename(input_file: str, output_file: str, mapping: str) -> None:
    rename_map = dict(pair.split(":", 1) for pair in mapping.split(","))
    result = renamer.rename_csv(input_file, output_file, rename_map)
    click.echo(renamer.summary(result))
    sys.exit(0 if not result.errors else 1)


# ---------------------------------------------------------------------------
# split
# ---------------------------------------------------------------------------
@main.command("split")
@click.argument("input_file")
@click.argument("output_dir")
@click.option("--column", default=None, help="Split by unique values in this column.")
@click.option("--chunk-size", default=None, type=int, help="Split into chunks of N rows.")
def cmd_split(input_file: str, output_dir: str, column: str | None, chunk_size: int | None) -> None:
    """Split INPUT_FILE into multiple CSV files in OUTPUT_DIR."""
    if column is None and chunk_size is None:
        raise click.UsageError("Provide --column or --chunk-size.")
    result = splitter.split_csv(input_file, output_dir, column=column, chunk_size=chunk_size)
    click.echo(splitter.summary(result))
    sys.exit(0 if not result.errors else 1)
