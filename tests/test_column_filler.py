"""Tests for csv_warden.column_filler."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_filler import fill_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows:
        return
    fn = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_fill_missing_with_value(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "", "age": ""}])
    result = fill_csv(str(src), str(out), {"name": "Unknown", "age": "0"})
    rows = _read(out)
    assert rows[1]["name"] == "Unknown"
    assert rows[1]["age"] == "0"
    assert result.fills["name"] == 1
    assert result.fills["age"] == 1


def test_no_fill_when_values_present(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}])
    result = fill_csv(str(src), str(out), {"name": "Unknown", "age": "0"})
    rows = _read(out)
    assert rows[0]["name"] == "Alice"
    assert result.fills == {}


def test_forward_fill(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"name": "Alice", "city": "NYC"},
        {"name": "Bob", "city": ""},
        {"name": "Carol", "city": ""},
    ])
    result = fill_csv(str(src), str(out), {"city": ""}, strategy="forward")
    rows = _read(out)
    assert rows[1]["city"] == "NYC"
    assert rows[2]["city"] == "NYC"
    assert result.fills["city"] == 2


def test_file_not_found(tmp_csv):
    out = tmp_csv / "out.csv"
    result = fill_csv("nonexistent.csv", str(out), {})
    assert result.errors
    assert "not found" in result.errors[0]


def test_rows_processed_count(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}, {"a": "2"}, {"a": ""}])
    result = fill_csv(str(src), str(out), {"a": "99"})
    assert result.rows_processed == 3


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": ""}])
    result = fill_csv(str(src), str(out), {"x": "default"})
    s = summary(result)
    assert "x" in s
    assert "1 value(s) filled" in s
