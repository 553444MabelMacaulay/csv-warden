"""Unit tests for csv_warden.column_crosser."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from csv_warden.column_crosser import cross_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path: Path):
    def _write(rows: list[list[str]], filename: str = "data.csv") -> str:
        p = tmp_path / filename
        with p.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerows(rows)
        return str(p)

    return _write


def _read(path: str) -> list[list[str]]:
    with open(path, newline="") as fh:
        return list(csv.reader(fh))


_DATA = [
    ["gender", "product", "score"],
    ["M", "A", "10"],
    ["F", "B", "20"],
    ["M", "B", "30"],
    ["F", "A", "40"],
    ["M", "A", "50"],
]


def test_basic_cross(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    result = cross_csv(src, "gender", "product", out)
    assert result.error is None
    assert sorted(result.row_labels) == ["F", "M"]
    assert sorted(result.col_labels) == ["A", "B"]


def test_output_file_written(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    cross_csv(src, "gender", "product", out)
    rows = _read(out)
    assert rows[0][0] == "gender\\product"
    assert "A" in rows[0] and "B" in rows[0]


def test_counts_correct(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    result = cross_csv(src, "gender", "product", out)
    assert result.table["M"]["A"] == 2
    assert result.table["M"]["B"] == 1
    assert result.table["F"]["A"] == 1
    assert result.table["F"]["B"] == 1


def test_missing_file(tmp_path):
    out = str(tmp_path / "cross.csv")
    result = cross_csv("no_such_file.csv", "gender", "product", out)
    assert result.error is not None
    assert "not found" in result.error


def test_missing_row_col(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    result = cross_csv(src, "nonexistent", "product", out)
    assert result.error is not None
    assert "nonexistent" in result.error


def test_missing_col_col(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    result = cross_csv(src, "gender", "nonexistent", out)
    assert result.error is not None


def test_summary_no_error(tmp_csv, tmp_path):
    src = tmp_csv(_DATA)
    out = str(tmp_path / "cross.csv")
    result = cross_csv(src, "gender", "product", out)
    s = summary(result)
    assert "Cross-tabulation" in s
    assert "gender" in s
    assert "product" in s


def test_summary_with_error():
    from csv_warden.column_crosser import CrossResult

    r = CrossResult(
        input_file="x.csv",
        row_col="a",
        col_col="b",
        output_file="out.csv",
        error="File not found: x.csv",
    )
    assert "[ERROR]" in summary(r)
