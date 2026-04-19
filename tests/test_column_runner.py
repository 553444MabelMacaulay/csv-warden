"""Tests for csv_warden.column_runner."""
import csv
import sys
from pathlib import Path

import pytest

from csv_warden.column_runner import run_column, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "input.csv"


def _write(p, rows):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_missing_file(tmp_path):
    r = run_column(str(tmp_path / "no.csv"), str(tmp_path / "out.csv"), "x", "echo {value}")
    assert r.errors
    assert "not found" in r.errors[0]


def test_column_not_found(tmp_csv, tmp_path):
    _write(tmp_csv, [{"a": "1"}])
    r = run_column(str(tmp_csv), str(tmp_path / "out.csv"), "z", "echo {value}")
    assert r.errors
    assert "not found" in r.errors[0]


@pytest.mark.skipif(sys.platform == "win32", reason="echo differs on Windows")
def test_basic_run_in_place(tmp_csv, tmp_path):
    _write(tmp_csv, [{"name": "alice"}, {"name": "bob"}])
    out = tmp_path / "out.csv"
    r = run_column(str(tmp_csv), str(out), "name", "echo hello_{value}")
    assert r.rows_processed == 2
    assert r.rows_failed == 0
    rows = _read(out)
    assert rows[0]["name"] == "hello_alice"
    assert rows[1]["name"] == "hello_bob"


@pytest.mark.skipif(sys.platform == "win32", reason="echo differs on Windows")
def test_new_column_created(tmp_csv, tmp_path):
    _write(tmp_csv, [{"val": "3"}, {"val": "7"}])
    out = tmp_path / "out.csv"
    r = run_column(str(tmp_csv), str(out), "val", "echo x{value}", new_column="val2")
    assert r.rows_processed == 2
    rows = _read(out)
    assert "val" in rows[0]
    assert "val2" in rows[0]
    assert rows[0]["val2"] == "x3"


@pytest.mark.skipif(sys.platform == "win32", reason="echo differs on Windows")
def test_summary_output(tmp_csv, tmp_path):
    _write(tmp_csv, [{"x": "1"}])
    out = tmp_path / "out.csv"
    r = run_column(str(tmp_csv), str(out), "x", "echo {value}")
    s = summary(r)
    assert "Processed" in s
    assert "x" in s
