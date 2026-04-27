"""Tests for csv_warden.column_reverser."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from csv_warden.column_reverser import reverse_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> Path:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_reverse_single_column(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"word": "hello"}, {"word": "world"}])
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["word"])
    assert result.error is None
    rows = _read(out)
    assert rows[0]["word"] == "olleh"
    assert rows[1]["word"] == "dlrow"


def test_reverse_preserves_other_columns(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}],
    )
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["name"])
    assert result.error is None
    rows = _read(out)
    assert rows[0]["id"] == "1"
    assert rows[0]["name"] == "ecilA"
    assert rows[1]["id"] == "2"
    assert rows[1]["name"] == "boB"


def test_reverse_multiple_columns(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [{"a": "abc", "b": "xyz"}],
    )
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["a", "b"])
    assert result.error is None
    rows = _read(out)
    assert rows[0]["a"] == "cba"
    assert rows[0]["b"] == "zyx"


def test_skipped_columns_reported(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"name": "Alice"}])
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["name", "missing_col"])
    assert result.error is None
    assert "missing_col" in result.skipped_columns


def test_missing_file_returns_error(tmp_csv):
    result = reverse_csv(
        str(tmp_csv / "no_such.csv"),
        str(tmp_csv / "out.csv"),
        columns=["col"],
    )
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_rows_affected_count(tmp_csv):
    src = _write(
        tmp_csv / "in.csv",
        [{"val": "abc"}, {"val": ""}, {"val": "xyz"}],
    )
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["val"])
    # empty string reversed is still empty — not changed
    assert result.rows_processed == 3
    assert result.rows_affected == 2


def test_summary_contains_key_info(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"x": "hi"}])
    out = tmp_csv / "out.csv"
    result = reverse_csv(str(src), str(out), columns=["x"])
    s = summary(result)
    assert "x" in s
    assert "Rows processed" in s
    assert "Rows affected" in s
