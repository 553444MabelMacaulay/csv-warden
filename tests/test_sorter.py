"""Tests for csv_warden.sorter."""
import csv
import os
import pytest
from pathlib import Path

from csv_warden.sorter import sort_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows:
        path.write_text("")
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_sort_ascending(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}])
    result = sort_csv(str(src), str(out), sort_columns=["name"], ascending=True)
    assert result.errors == []
    assert result.rows_sorted == 3
    rows = _read(out)
    assert [r["name"] for r in rows] == ["Alice", "Bob", "Charlie"]


def test_sort_descending(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"age": "30"}, {"age": "10"}, {"age": "20"}])
    result = sort_csv(str(src), str(out), sort_columns=["age"], ascending=False)
    assert result.errors == []
    rows = _read(out)
    assert [r["age"] for r in rows] == ["30", "20", "10"]


def test_sort_multiple_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    data = [
        {"dept": "B", "name": "Zara"},
        {"dept": "A", "name": "Mike"},
        {"dept": "A", "name": "Anna"},
    ]
    _write(src, data)
    result = sort_csv(str(src), str(out), sort_columns=["dept", "name"])
    assert result.errors == []
    rows = _read(out)
    assert [(r["dept"], r["name"]) for r in rows] == [
        ("A", "Anna"), ("A", "Mike"), ("B", "Zara")
    ]


def test_missing_file_returns_error(tmp_csv):
    result = sort_csv("/no/such/file.csv", str(tmp_csv / "out.csv"), ["col"])
    assert any("not found" in e for e in result.errors)
    assert result.rows_sorted == 0


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice"}])
    result = sort_csv(str(src), str(out), sort_columns=["nonexistent"])
    assert any("nonexistent" in e for e in result.errors)


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1"}, {"x": "2"}])
    result = sort_csv(str(src), str(out), sort_columns=["x"])
    s = summary(result)
    assert "ascending" in s
    assert "x" in s
    assert "2" in s
