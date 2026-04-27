"""Integration tests for regex-extract: multi-group, fill-value, and round-trip."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture()
def multi_col_csv(tmp_path: Path) -> str:
    p = tmp_path / "multi.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "contact"])
        writer.writerow(["1", "Alice", "alice@example.com"])
        writer.writerow(["2", "Bob", "bob@work.org"])
        writer.writerow(["3", "Carol", "not-an-email"])
    return str(p)


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_all_original_columns_preserved(multi_col_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    _run(["regex-extract", multi_col_csv, out,
          "--column", "contact",
          "--pattern", r"(?P<user>[^@]+)@(?P<domain>.+)"])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert "id" in rows[0]
    assert "name" in rows[0]
    assert "contact" in rows[0]


def test_fill_value_applied_to_non_matching_rows(multi_col_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    _run(["regex-extract", multi_col_csv, out,
          "--column", "contact",
          "--pattern", r"(?P<user>[^@]+)@(?P<domain>.+)",
          "--fill-value", "UNKNOWN"])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    carol = next(r for r in rows if r["name"] == "Carol")
    assert carol["user"] == "UNKNOWN"
    assert carol["domain"] == "UNKNOWN"


def test_matched_count_in_summary(multi_col_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    result = _run(["regex-extract", multi_col_csv, out,
                   "--column", "contact",
                   "--pattern", r"(?P<user>[^@]+)@(?P<domain>.+)"])
    assert "Rows matched: 2" in result.output
    assert "Rows total  : 3" in result.output


def test_new_columns_listed_in_summary(multi_col_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    result = _run(["regex-extract", multi_col_csv, out,
                   "--column", "contact",
                   "--pattern", r"(?P<user>[^@]+)@(?P<domain>.+)"])
    assert "user" in result.output
    assert "domain" in result.output
