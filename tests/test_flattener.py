"""Tests for csv_warden.flattener."""
import csv
import json
import pytest
from pathlib import Path
from csv_warden.flattener import flatten_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, fieldnames=None):
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_flatten_json_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"id": "1", "meta": json.dumps({"city": "NY", "age": 30})},
        {"id": "2", "meta": json.dumps({"city": "LA", "age": 25})},
    ])
    result = flatten_csv(str(src), str(out))
    assert result.rows_processed == 2
    assert "meta" in result.columns_expanded
    rows = _read(out)
    assert rows[0]["meta.city"] == "NY"
    assert rows[1]["meta.age"] == "25"


def test_non_json_column_untouched(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ])
    result = flatten_csv(str(src), str(out))
    assert result.columns_expanded == []
    rows = _read(out)
    assert rows[0]["name"] == "Alice"


def test_partial_json_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"id": "1", "data": json.dumps({"x": 1})},
        {"id": "2", "data": "not-json"},
    ])
    result = flatten_csv(str(src), str(out))
    assert result.rows_processed == 2
    rows = _read(out)
    assert rows[0]["data.x"] == "1"
    assert rows[1]["data.x"] == ""


def test_missing_file(tmp_csv):
    result = flatten_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"))
    assert result.errors
    assert "not found" in result.errors[0]


def test_specific_columns_only(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"id": "1", "a": json.dumps({"k": 1}), "b": json.dumps({"m": 2})},
    ])
    result = flatten_csv(str(src), str(out), columns=["a"])
    assert "a" in result.columns_expanded
    assert "b" not in result.columns_expanded
    rows = _read(out)
    assert "a.k" in rows[0]
    assert "b.m" not in rows[0]


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "info": json.dumps({"val": 9})}])
    result = flatten_csv(str(src), str(out))
    s = summary(result)
    assert "Rows processed" in s
    assert "info" in s
