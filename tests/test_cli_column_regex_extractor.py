"""CLI integration tests for the regex-extract sub-command."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture()
def simple_csv(tmp_path: Path) -> str:
    p = tmp_path / "data.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "timestamp"])
        writer.writerow(["1", "2024-07-04T12:30:00"])
        writer.writerow(["2", "2023-01-20T08:00:00"])
    return str(p)


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_regex_extract_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    result = _run(["regex-extract", simple_csv, out,
                   "--column", "timestamp",
                   "--pattern", r"(?P<date>\d{4}-\d{2}-\d{2})"])
    assert result.exit_code == 0


def test_regex_extract_output_has_new_column(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    _run(["regex-extract", simple_csv, out,
          "--column", "timestamp",
          "--pattern", r"(?P<date>\d{4}-\d{2}-\d{2})"])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert "date" in rows[0]
    assert rows[0]["date"] == "2024-07-04"


def test_regex_extract_drop_original(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    _run(["regex-extract", simple_csv, out,
          "--column", "timestamp",
          "--pattern", r"(?P<date>\d{4}-\d{2}-\d{2})",
          "--drop-original"])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert "timestamp" not in rows[0]
    assert "date" in rows[0]


def test_regex_extract_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    result = _run(["regex-extract", "/no/such/file.csv", out,
                   "--column", "x",
                   "--pattern", r"(?P<a>\d+)"])
    assert result.exit_code == 1


def test_regex_extract_summary_shows_match_count(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    result = _run(["regex-extract", simple_csv, out,
                   "--column", "timestamp",
                   "--pattern", r"(?P<date>\d{4}-\d{2}-\d{2})"])
    assert "Rows matched" in result.output
    assert "2" in result.output
