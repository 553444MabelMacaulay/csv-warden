"""Tests for csv_warden.column_padder."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_padder import pad_csv, summary


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


def test_pad_left(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bo", "age": "5"}])
    result = pad_csv(str(src), str(out), widths={"name": 8}, align="left")
    assert not result.errors
    rows = _read(out)
    assert rows[0]["name"] == "Alice   "
    assert rows[1]["name"] == "Bo      "


def test_pad_right(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"code": "42"}, {"code": "7"}])
    result = pad_csv(str(src), str(out), widths={"code": 5}, align="right")
    assert not result.errors
    rows = _read(out)
    assert rows[0]["code"] == "   42"
    assert rows[1]["code"] == "    7"


def test_rows_affected_count(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "hi"}, {"val": "hello world"}])
    result = pad_csv(str(src), str(out), widths={"val": 5})
    # "hi" -> padded, "hello world" already longer so ljust won't change it
    assert result.rows_affected == 1


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = pad_csv(str(tmp_csv / "nope.csv"), str(out), widths={"x": 5})
    assert result.errors
    assert "not found" in result.errors[0]


def test_unknown_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = pad_csv(str(src), str(out), widths={"z": 5})
    assert any("z" in e for e in result.errors)


def test_invalid_align(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = pad_csv(str(src), str(out), widths={"a": 5}, align="center")
    assert result.errors


def test_custom_fill_char(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "7"}])
    result = pad_csv(str(src), str(out), widths={"id": 4}, align="right", fill_char="0")
    assert not result.errors
    rows = _read(out)
    assert rows[0]["id"] == "0007"


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "a"}])
    result = pad_csv(str(src), str(out), widths={"x": 3})
    s = summary(result)
    assert "x" in s
    assert "Rows affected" in s
