"""Tests for csv_warden.column_date_parser."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_date_parser import parse_dates, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_basic_date_conversion(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "date": "2024-01-15"}, {"id": "2", "date": "2024-06-30"}], ["id", "date"])
    r = parse_dates(str(src), str(out), "date", "%Y-%m-%d", "%d/%m/%Y")
    assert r.rows_converted == 2
    assert r.rows_failed == 0
    rows = _read(out)
    assert rows[0]["date"] == "15/01/2024"
    assert rows[1]["date"] == "30/06/2024"


def test_failed_rows_coerced(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"date": "not-a-date"}, {"date": "2024-03-01"}], ["date"])
    r = parse_dates(str(src), str(out), "date", "%Y-%m-%d", "%d/%m/%Y")
    assert r.rows_failed == 1
    assert r.rows_converted == 1
    assert len(r.errors) == 1


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice"}], ["name"])
    r = parse_dates(str(src), str(out), "date", "%Y-%m-%d", "%d/%m/%Y")
    assert any("not found" in e for e in r.errors)
    assert r.rows_converted == 0


def test_file_not_found(tmp_csv):
    r = parse_dates(str(tmp_csv / "missing.csv"), str(tmp_csv / "out.csv"), "date", "%Y-%m-%d", "%d/%m/%Y")
    assert any("not found" in e for e in r.errors)


def test_output_file_written(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"ts": "01-Jan-2023"}], ["ts"])
    parse_dates(str(src), str(out), "ts", "%d-%b-%Y", "%Y/%m/%d")
    assert out.exists()
    rows = _read(out)
    assert rows[0]["ts"] == "2023/01/01"


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"d": "2020-05-10"}], ["d"])
    r = parse_dates(str(src), str(out), "d", "%Y-%m-%d", "%m-%d-%Y")
    s = summary(r)
    assert "Converted" in s
    assert "d" in s
