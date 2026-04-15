"""Tests for csv_warden.profiler."""

from __future__ import annotations

import csv
import pytest
from pathlib import Path

from csv_warden.profiler import profile_csv, ProfileReport, ColumnProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_csv(tmp_path: Path):
    """Return a factory that writes rows to a temp CSV and returns its path."""

    def _write(headers: list[str], rows: list[list[str]]) -> str:
        p = tmp_path / "test.csv"
        with p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(headers)
            w.writerows(rows)
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_basic_profile(tmp_csv):
    path = tmp_csv(
        ["name", "age"],
        [["Alice", "30"], ["Bob", "25"], ["Charlie", "30"]],
    )
    report = profile_csv(path)
    assert isinstance(report, ProfileReport)
    assert report.row_count == 3
    assert report.column_count == 2
    assert "name" in report.columns
    assert "age" in report.columns


def test_fill_rate_full(tmp_csv):
    path = tmp_csv(["x"], [["a"], ["b"], ["c"]])
    col = profile_csv(path).columns["x"]
    assert col.fill_rate == 100.0
    assert col.missing == 0


def test_fill_rate_with_missing(tmp_csv):
    path = tmp_csv(["x"], [["a"], [""], ["c"]])
    col = profile_csv(path).columns["x"]
    assert col.missing == 1
    assert col.fill_rate == pytest.approx(66.67, rel=1e-2)


def test_unique_count(tmp_csv):
    path = tmp_csv(["v"], [["a"], ["a"], ["b"]])
    col = profile_csv(path).columns["v"]
    assert col.unique == 2


def test_min_max_length(tmp_csv):
    path = tmp_csv(["w"], [["hi"], ["hello"], ["yo"]])
    col = profile_csv(path).columns["w"]
    assert col.min_length == 2
    assert col.max_length == 5


def test_top_values(tmp_csv):
    path = tmp_csv(["c"], [["x"], ["x"], ["y"], ["z"]])
    col = profile_csv(path, top_n=2).columns["c"]
    values = [v for v, _ in col.top_values]
    assert "x" in values


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        profile_csv("/nonexistent/path/data.csv")


def test_summary_output(tmp_csv):
    path = tmp_csv(["id", "val"], [["1", "foo"], ["2", ""]])
    report = profile_csv(path)
    summary = report.summary()
    assert "id" in summary
    assert "val" in summary
    assert "Rows" in summary
