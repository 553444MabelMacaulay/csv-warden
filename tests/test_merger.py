"""Tests for csv_warden.merger."""

import csv
from pathlib import Path

import pytest

from csv_warden.merger import merge_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    """Return a helper that writes a CSV and gives back its path string."""

    def _write(name: str, rows: list[list]) -> str:
        p = tmp_path / name
        with p.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerows(rows)
        return str(p)

    return _write


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_merge_two_compatible_files(tmp_csv, tmp_path):
    f1 = tmp_csv("a.csv", [["id", "name"], ["1", "Alice"], ["2", "Bob"]])
    f2 = tmp_csv("b.csv", [["id", "name"], ["3", "Carol"]])
    out = str(tmp_path / "merged.csv")

    result = merge_csv([f1, f2], out)

    assert result.total_rows_written == 3
    assert len(result.errors) == 0
    assert len(result.skipped_files) == 0
    rows = _read_csv(out)
    assert [r["name"] for r in rows] == ["Alice", "Bob", "Carol"]


def test_merge_missing_file_is_skipped(tmp_csv, tmp_path):
    f1 = tmp_csv("good.csv", [["x"], ["1"]])
    out = str(tmp_path / "out.csv")

    result = merge_csv([f1, "/nonexistent/missing.csv"], out)

    assert result.total_rows_written == 1
    assert "/nonexistent/missing.csv" in result.skipped_files
    assert any("not found" in e.lower() for e in result.errors)


def test_merge_column_mismatch_skipped(tmp_csv, tmp_path):
    f1 = tmp_csv("c1.csv", [["a", "b"], ["1", "2"]])
    f2 = tmp_csv("c2.csv", [["a", "c"], ["3", "4"]])
    out = str(tmp_path / "out.csv")

    result = merge_csv([f1, f2], out, require_same_columns=True)

    assert result.total_rows_written == 1
    assert str(f2) in result.skipped_files
    assert any("mismatch" in e.lower() for e in result.errors)


def test_merge_column_mismatch_allowed(tmp_csv, tmp_path):
    f1 = tmp_csv("d1.csv", [["a", "b"], ["1", "2"]])
    f2 = tmp_csv("d2.csv", [["a", "b"], ["3", "4"]])
    out = str(tmp_path / "out.csv")

    result = merge_csv([f1, f2], out, require_same_columns=False)

    assert result.total_rows_written == 2
    assert len(result.skipped_files) == 0


def test_merge_all_invalid_inputs(tmp_path):
    out = str(tmp_path / "out.csv")
    result = merge_csv(["/no/file.csv"], out)

    assert result.total_rows_written == 0
    assert any("no valid" in e.lower() for e in result.errors)


def test_summary_contains_key_info(tmp_csv, tmp_path):
    f1 = tmp_csv("e.csv", [["col"], ["val"]])
    out = str(tmp_path / "out.csv")
    result = merge_csv([f1], out)
    s = summary(result)

    assert "Rows written" in s
    assert "1" in s
    assert out in s
