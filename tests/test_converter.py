"""Tests for csv_warden.converter."""
import csv
import json
from pathlib import Path

import pytest

from csv_warden.converter import convert_csv, summary, SUPPORTED_FORMATS


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows:
        path.write_text("")
        return
    fn = fieldnames or list(rows[0].keys())
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fn)
        writer.writeheader()
        writer.writerows(rows)


def test_convert_to_json(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "data.json"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    result = convert_csv(str(src), str(out), "json")
    assert result.success
    assert result.rows_written == 2
    data = json.loads(out.read_text())
    assert data[0]["name"] == "Alice"
    assert data[1]["age"] == "25"


def test_convert_to_tsv(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "data.tsv"
    _write(src, [{"city": "NYC", "pop": "8M"}, {"city": "LA", "pop": "4M"}])
    result = convert_csv(str(src), str(out), "tsv")
    assert result.success
    assert result.rows_written == 2
    content = out.read_text()
    assert "\t" in content
    assert "NYC" in content


def test_unsupported_format(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "data.xml"
    _write(src, [{"a": "1"}])
    result = convert_csv(str(src), str(out), "xml")
    assert not result.success
    assert any("Unsupported" in e for e in result.errors)


def test_missing_input_file(tmp_csv):
    result = convert_csv(str(tmp_csv / "missing.csv"), str(tmp_csv / "out.json"), "json")
    assert not result.success
    assert any("not found" in e for e in result.errors)


def test_empty_csv(tmp_csv):
    src = tmp_csv / "empty.csv"
    src.write_text("")
    result = convert_csv(str(src), str(tmp_csv / "out.json"), "json")
    assert not result.success
    assert any("empty" in e.lower() for e in result.errors)


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "data.json"
    _write(src, [{"x": "1", "y": "2"}])
    result = convert_csv(str(src), str(out), "json")
    s = summary(result)
    assert "json" in s.lower()
    assert "1" in s  # rows_written


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "tsv" in SUPPORTED_FORMATS
