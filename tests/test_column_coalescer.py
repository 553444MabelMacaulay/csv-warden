"""Tests for csv_warden.column_coalescer."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_coalescer import coalesce_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_fills_missing_from_first_fallback(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "", "b": "hello", "c": "world"}, {"a": "keep", "b": "x", "c": "y"}], ["a", "b", "c"])
    result = coalesce_csv(str(src), str(out), "a", ["b", "c"])
    assert result.rows_filled == 1
    rows = _read(out)
    assert rows[0]["a"] == "hello"
    assert rows[1]["a"] == "keep"


def test_falls_through_to_second_fallback(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "", "b": "", "c": "fallback2"}], ["a", "b", "c"])
    result = coalesce_csv(str(src), str(out), "a", ["b", "c"])
    rows = _read(out)
    assert rows[0]["a"] == "fallback2"
    assert result.rows_filled == 1


def test_no_fill_when_target_present(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "present", "b": "other"}], ["a", "b"])
    result = coalesce_csv(str(src), str(out), "a", ["b"])
    assert result.rows_filled == 0
    rows = _read(out)
    assert rows[0]["a"] == "present"


def test_missing_file_returns_error(tmp_csv):
    result = coalesce_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), "a", ["b"])
    assert result.errors
    assert "not found" in result.errors[0]


def test_missing_target_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    result = coalesce_csv(str(src), str(out), "z", ["a"])
    assert any("Target column" in e for e in result.errors)


def test_missing_fallback_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": ""}], ["a"])
    result = coalesce_csv(str(src), str(out), "a", ["nonexistent"])
    assert any("Fallback" in e for e in result.errors)


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "", "b": "v"}], ["a", "b"])
    result = coalesce_csv(str(src), str(out), "a", ["b"])
    s = summary(result)
    assert "Rows filled" in s
    assert "a" in s
