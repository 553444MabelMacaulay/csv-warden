"""CLI sub-command: map — replace column values using a mapping."""
from __future__ import annotations

import json
import sys

import click

from csv_warden.column_mapper import map_csv, summary


def register(main: click.Group) -> None:
    main.add_command(cmd_map)


@click.command("map")
@click.argument("input_file")
@click.argument("output_file")
@click.option("--column", required=True, help="Column whose values to map.")
@click.option(
    "--mapping",
    required=True,
    help='JSON object of old->new value pairs, e.g. \'{"A":"Active"}\'.',
)
@click.option("--default", default=None, help="Replacement for unmapped values (omit to leave unchanged).")
def cmd_map(input_file: str, output_file: str, column: str, mapping: str, default):
    """Map values in COLUMN of INPUT_FILE using a JSON mapping and write to OUTPUT_FILE."""
    try:
        mapping_dict = json.loads(mapping)
    except json.JSONDecodeError as exc:
        click.echo(f"Invalid JSON mapping: {exc}", err=True)
        sys.exit(1)

    result = map_csv(input_file, output_file, column, mapping_dict, default=default)

    if result.errors:
        for e in result.errors:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(summary(result))
