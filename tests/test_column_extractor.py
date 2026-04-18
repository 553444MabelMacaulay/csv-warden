"""Tests for csv_warden.column_extractor."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_extractor import extract_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    fn = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_extract_with_pattern(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"email": "user@example.com"}, {"email": "admin@test.org"}])
    result = extract_csv(str(src), str(out), column="email", new_column="domain", pattern=r"@(.+)$", group=1)
    assert result.rows_extracted == 2
    rows = _read(out)
    assert rows[0]["domain"] == "example.com"
    assert rows[1]["domain"] == "test.org"


def test_extract_with_slice(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"code": "ABC123"}, {"code": "XYZ999"}])
    result = extract_csv(str(src), str(out), column="code", new_column="prefix", start=0, end=3)
    assert result.rows_extracted == 2
    rows = _read(out)
    assert rows[0]["prefix"] == "ABC"
    assert rows[1]["prefix"] == "XYZ"


def test_default_new_column_name(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "John Doe"}])
    result = extract_csv(str(src), str(out), column="name", pattern=r"(\w+)$", group=1)
    assert result.new_column == "name_extracted"
    rows = _read(out)
    assert "name_extracted" in rows[0]


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = extract_csv(str(tmp_csv / "nope.csv"), str(out), column="x")
    assert result.errors
    assert "not found" in result.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = extract_csv(str(src), str(out), column="z", pattern=r"(\d+)")
    assert any("not found" in e for e in result.errors)


def test_pattern_no_match_gives_empty(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "hello"}])
    result = extract_csv(str(src), str(out), column="val", new_column="num", pattern=r"(\d+)", group=1)
    assert result.rows_extracted == 0
    rows = _read(out)
    assert rows[0]["num"] == ""


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "abc"}])
    result = extract_csv(str(src), str(out), column="x", new_column="y", start=0, end=1)
    s = summary(result)
    assert "x" in s
    assert "y" in s
