"""CLI integration tests for the 'split' sub-command."""

import csv
import os
import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture()
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["region", "score"])
        writer.writeheader()
        writer.writerows([
            {"region": "north", "score": "1"},
            {"region": "south", "score": "2"},
            {"region": "north", "score": "3"},
        ])
    return str(p), str(tmp_path / "out")


def test_split_by_column_exit_zero(simple_csv):
    src, out = simple_csv
    runner = CliRunner()
    result = runner.invoke(main, ["split", src, out, "--column", "region"])
    assert result.exit_code == 0


def test_split_output_contains_chunks(simple_csv):
    src, out = simple_csv
    runner = CliRunner()
    result = runner.invoke(main, ["split", src, out, "--column", "region"])
    assert "Chunks" in result.output
    assert "north.csv" in result.output


def test_split_by_chunk_size_exit_zero(simple_csv):
    src, out = simple_csv
    runner = CliRunner()
    result = runner.invoke(main, ["split", src, out, "--chunk-size", "2"])
    assert result.exit_code == 0
    assert "chunk_0001.csv" in result.output


def test_split_missing_file_exits_one(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["split", str(tmp_path / "nope.csv"), str(tmp_path / "out"), "--column", "x"]
    )
    assert result.exit_code == 1


def test_split_no_mode_exits_one(simple_csv):
    src, out = simple_csv
    runner = CliRunner()
    result = runner.invoke(main, ["split", src, out])
    assert result.exit_code != 0
