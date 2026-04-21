"""CLI integration tests for the 'cross' sub-command."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture()
def simple_csv(tmp_path: Path) -> str:
    p = tmp_path / "data.csv"
    rows = [
        ["dept", "level", "salary"],
        ["Eng", "junior", "60000"],
        ["Eng", "senior", "90000"],
        ["HR", "junior", "55000"],
        ["HR", "senior", "80000"],
        ["Eng", "junior", "62000"],
    ]
    with p.open("w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return str(p)


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args)


def test_cross_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "cross.csv")
    result = _run(["cross", simple_csv, "--row-col", "dept", "--col-col", "level", "--output", out])
    assert result.exit_code == 0


def test_cross_output_has_correct_headers(simple_csv, tmp_path):
    out = str(tmp_path / "cross.csv")
    _run(["cross", simple_csv, "--row-col", "dept", "--col-col", "level", "--output", out])
    with open(out, newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    assert "junior" in header
    assert "senior" in header


def test_cross_output_counts(simple_csv, tmp_path):
    out = str(tmp_path / "cross.csv")
    _run(["cross", simple_csv, "--row-col", "dept", "--col-col", "level", "--output", out])
    with open(out, newline="") as fh:
        rows = list(csv.reader(fh))
    # Eng row should show 2 for junior
    header = rows[0]
    junior_idx = header.index("junior")
    eng_row = next(r for r in rows[1:] if r[0] == "Eng")
    assert eng_row[junior_idx] == "2"


def test_cross_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "cross.csv")
    result = _run(["cross", "no_such.csv", "--row-col", "dept", "--col-col", "level", "--output", out])
    assert result.exit_code == 1


def test_cross_summary_mentions_columns(simple_csv, tmp_path):
    out = str(tmp_path / "cross.csv")
    result = _run(["cross", simple_csv, "--row-col", "dept", "--col-col", "level", "--output", out])
    assert "dept" in result.output
    assert "level" in result.output
