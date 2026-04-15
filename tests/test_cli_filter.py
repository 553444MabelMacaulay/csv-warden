"""CLI integration tests for the `filter` sub-command."""
import csv
from pathlib import Path

import pytest

from csv_warden.cli import build_parser, main


@pytest.fixture()
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with p.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "status"])
        writer.writeheader()
        writer.writerows(
            [{"name": "alice", "status": "active"}, {"name": "bob", "status": "inactive"}]
        )
    return str(p)


def test_filter_exit_zero(simple_csv, tmp_path, capsys):
    out = str(tmp_path / "out.csv")
    rc = main(["filter", simple_csv, "--output", out, "--column", "status", "--value", "active"])
    assert rc == 0


def test_filter_output_contains_only_matching(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    main(["filter", simple_csv, "--output", out, "--column", "status", "--value", "active"])
    rows = list(csv.DictReader(open(out)))
    assert all(r["status"] == "active" for r in rows)
    assert len(rows) == 1


def test_filter_exclude_flag(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    main(["filter", simple_csv, "--output", out, "--column", "status", "--value", "active", "--exclude"])
    rows = list(csv.DictReader(open(out)))
    assert rows[0]["name"] == "bob"


def test_filter_missing_file_exits_one(tmp_path, capsys):
    rc = main(["filter", str(tmp_path / "ghost.csv"), "--column", "x", "--value", "1"])
    assert rc == 1


def test_filter_missing_column_exits_one(simple_csv, capsys):
    rc = main(["filter", simple_csv, "--column", "nonexistent", "--value", "x"])
    assert rc == 1
