"""CLI integration tests for the condense-col sub-command."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["first", "last", "age"])
        w.writeheader()
        w.writerows([
            {"first": "Alice", "last": "Smith", "age": "30"},
            {"first": "Bob", "last": "Jones", "age": "25"},
        ])
    return p


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "csv_warden", *args],
        capture_output=True,
        text=True,
    )


def test_condense_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run([
        "condense-col", str(simple_csv), str(out),
        "--template", "{first} {last}",
        "--new-column", "full_name",
    ])
    assert r.returncode == 0


def test_condense_col_output_has_new_column(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "condense-col", str(simple_csv), str(out),
        "--template", "{first} {last}",
        "--new-column", "full_name",
    ])
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["full_name"] == "Alice Smith"
    assert rows[1]["full_name"] == "Bob Jones"


def test_condense_col_drop_sources(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "condense-col", str(simple_csv), str(out),
        "--template", "{first} {last}",
        "--new-column", "full_name",
        "--drop-sources",
    ])
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert "first" not in rows[0]
    assert "last" not in rows[0]
    assert "age" in rows[0]


def test_condense_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = _run([
        "condense-col", str(tmp_path / "ghost.csv"), str(out),
        "--template", "{a}",
        "--new-column", "x",
    ])
    assert r.returncode == 1


def test_condense_col_summary_in_stdout(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run([
        "condense-col", str(simple_csv), str(out),
        "--template", "{first}-{age}",
        "--new-column", "tag",
    ])
    assert "Rows processed" in r.stdout
    assert "tag" in r.stdout
