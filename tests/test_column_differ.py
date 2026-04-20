"""Tests for csv_warden.column_differ."""
import csv
import os
from pathlib import Path

import pytest

from csv_warden.column_differ import diff_columns, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_flag_mode_marks_differences(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"a": "hello", "b": "hello"},
        {"a": "foo",   "b": "bar"},
        {"a": "x",     "b": "x"},
    ])
    result = diff_columns(str(src), "a", "b", str(out), mode="flag")
    assert result.rows_total == 3
    assert result.rows_same == 2
    assert result.rows_different == 1
    rows = _read(out)
    assert rows[0]["__diff__"] == "False"
    assert rows[1]["__diff__"] == "True"


def test_delta_mode_numeric(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"x": "10", "y": "3"},
        {"x": "5",  "y": "5"},
    ])
    result = diff_columns(str(src), "x", "y", str(out), mode="delta")
    rows = _read(out)
    assert float(rows[0]["__diff__"]) == pytest.approx(7.0)
    assert float(rows[1]["__diff__"]) == pytest.approx(0.0)
    assert result.rows_different == 1


def test_delta_mode_non_numeric_gives_empty(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "hello", "b": "world"}])
    result = diff_columns(str(src), "a", "b", str(out), mode="delta")
    rows = _read(out)
    assert rows[0]["__diff__"] == ""


def test_missing_file_returns_error(tmp_csv):
    result = diff_columns("no_such.csv", "a", "b", str(tmp_csv / "out.csv"))
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = diff_columns(str(src), "a", "z", str(out))
    assert any("z" in e for e in result.errors)


def test_unknown_mode_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = diff_columns(str(src), "a", "b", str(out), mode="bad")
    assert result.errors


def test_custom_diff_column_name(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"p": "1", "q": "2"}])
    diff_columns(str(src), "p", "q", str(out), diff_col="changed")
    rows = _read(out)
    assert "changed" in rows[0]


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "1"}])
    result = diff_columns(str(src), "a", "b", str(out))
    s = summary(result)
    assert "a" in s
    assert "b" in s
    assert "1" in s  # row counts
