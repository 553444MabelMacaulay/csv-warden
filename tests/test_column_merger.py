"""Tests for csv_warden.column_merger."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_merger import merge_columns, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_merge_basic(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"first": "John", "last": "Doe", "age": "30"}])
    result = merge_columns(str(src), str(out), ["first", "last"], "full_name")
    assert result.rows_processed == 1
    assert not result.errors
    rows = _read(out)
    assert rows[0]["full_name"] == "John Doe"
    assert "first" in rows[0]
    assert "last" in rows[0]


def test_merge_custom_separator(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "foo", "b": "bar"}])
    result = merge_columns(str(src), str(out), ["a", "b"], "combined", separator="-")
    rows = _read(out)
    assert rows[0]["combined"] == "foo-bar"


def test_merge_drop_originals(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"first": "Jane", "last": "Smith", "id": "1"}])
    result = merge_columns(str(src), str(out), ["first", "last"], "full_name", drop_originals=True)
    rows = _read(out)
    assert "first" not in rows[0]
    assert "last" not in rows[0]
    assert rows[0]["full_name"] == "Jane Smith"
    assert rows[0]["id"] == "1"


def test_merge_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = merge_columns(str(tmp_csv / "nope.csv"), str(out), ["a"], "b")
    assert result.errors
    assert "not found" in result.errors[0]


def test_merge_missing_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1"}])
    result = merge_columns(str(src), str(out), ["x", "y"], "z")
    assert result.errors
    assert "y" in result.errors[0]


def test_summary_ok(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = merge_columns(str(src), str(out), ["a", "b"], "c")
    s = summary(result)
    assert "OK" in s
    assert "c" in s


def test_multiple_rows(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    data = [{"city": "New York", "country": "US"}, {"city": "Paris", "country": "FR"}]
    _write(src, data)
    result = merge_columns(str(src), str(out), ["city", "country"], "location", separator=", ")
    assert result.rows_processed == 2
    rows = _read(out)
    assert rows[0]["location"] == "New York, US"
    assert rows[1]["location"] == "Paris, FR"
