"""Tests for csv_warden.deduplicator."""
import csv
import pytest
from pathlib import Path

from csv_warden.deduplicator import deduplicate_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[list[str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return path


def test_no_duplicates(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["id", "name"], ["1", "Alice"], ["2", "Bob"]])
    out = tmp_csv / "out.csv"
    result = deduplicate_csv(str(src), str(out))
    assert result.duplicates_removed == 0
    assert result.output_rows == 2
    assert result.errors == []


def test_removes_exact_duplicates(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [["id", "name"], ["1", "Alice"], ["1", "Alice"], ["2", "Bob"]],
    )
    out = tmp_csv / "out.csv"
    result = deduplicate_csv(str(src), str(out))
    assert result.duplicates_removed == 1
    assert result.output_rows == 2
    assert result.input_rows == 3


def test_output_file_written_correctly(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [["id", "val"], ["1", "x"], ["1", "x"], ["2", "y"]],
    )
    out = tmp_csv / "out.csv"
    deduplicate_csv(str(src), str(out))
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert rows[0]["id"] == "1"
    assert rows[1]["id"] == "2"


def test_subset_deduplication(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [["id", "name", "score"], ["1", "Alice", "90"], ["1", "Alice", "85"], ["2", "Bob", "70"]],
    )
    out = tmp_csv / "out.csv"
    result = deduplicate_csv(str(src), str(out), subset=["id", "name"])
    assert result.duplicates_removed == 1
    assert result.output_rows == 2


def test_keep_last(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [["id", "val"], ["1", "first"], ["1", "last"]],
    )
    out = tmp_csv / "out.csv"
    deduplicate_csv(str(src), str(out), keep="last")
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["val"] == "last"


def test_file_not_found(tmp_csv):
    result = deduplicate_csv("nonexistent.csv", str(tmp_csv / "out.csv"))
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_invalid_subset_column(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["id", "name"], ["1", "Alice"]])
    out = tmp_csv / "out.csv"
    result = deduplicate_csv(str(src), str(out), subset=["missing_col"])
    assert result.errors
    assert "missing_col" in result.errors[0]


def test_summary_output(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [["id"], ["1"], ["1"], ["2"]],
    )
    out = tmp_csv / "out.csv"
    result = deduplicate_csv(str(src), str(out))
    text = summary(result)
    assert "Duplicates" in text
    assert "1" in text
