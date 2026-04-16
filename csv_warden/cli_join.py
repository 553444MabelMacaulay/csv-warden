"""Join command wired into cli.py via this helper module."""
from pathlib import Path
import click
from csv_warden.joiner import join_csv, summary


def register(main):
    @main.command("join")
    @click.argument("left", type=click.Path())
    @click.argument("right", type=click.Path())
    @click.option("--key", required=True, help="Column name to join on")
    @click.option("--output", required=True, type=click.Path(), help="Output CSV path")
    @click.option(
        "--join-type",
        default="inner",
        type=click.Choice(["inner", "left", "right"]),
        show_default=True,
        help="Type of join to perform",
    )
    def cmd_join(left, right, key, output, join_type):
        """Join two CSV files on a common key column."""
        result = join_csv(
            Path(left),
            Path(right),
            key,
            Path(output),
            join_type=join_type,
        )
        click.echo(summary(result))
        if result.errors:
            raise SystemExit(1)
