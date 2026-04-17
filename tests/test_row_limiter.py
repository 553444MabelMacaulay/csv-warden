"""Tests for csv_warden.row_limiter."""
import csv
import pytest
from pathlib import Path
from csv_warden.row_limiter import limit_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None) -> Path:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_head_returns_first_n(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": str(i)} for i in range(10)])
    out = tmp_csv / "out.csv"
    result = limit_csv(str(src), str(out), n=3, mode="head")
    assert result.rows_in == 10
    assert result.rows_out == 3
    rows = _read(out)
    assert [r["a"] for r in rows] == ["0", "1", "2"]


def test_tail_returns_last_n(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": str(i)} for i in range(10)])
    out = tmp_csv / "out.csv"
    result = limit_csv(str(src), str(out), n=3, mode="tail")
    assert result.rows_out == 3
    rows = _read(out)
    assert [r["a"] for r in rows] == ["7", "8", "9"]


def test_n_larger_than_rows(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": str(i)} for i in range(5)])
    out = tmp_csv / "out.csv"
    result = limit_csv(str(src), str(out), n=100, mode="head")
    assert result.rows_out == 5


def test_tail_n_larger_than_rows(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": str(i)} for i in range(5)])
    out = tmp_csv / "out.csv"
    result = limit_csv(str(src), str(out), n=100, mode="tail")
    assert result.rows_out == 5


def test_missing_file_sets_error(tmp_csv):
    out = tmp_csv / "out.csv"
    result = limit_csv(str(tmp_csv / "missing.csv"), str(out), n=5)
    assert result.errors
    assert not out.exists()


def test_summary_contains_mode(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"x": "1"}])
    out = tmp_csv / "out.csv"
    result = limit_csv(str(src), str(out), n=1, mode="tail")
    s = summary(result)
    assert "tail" in s
    assert "Rows out" in s
