"""Tests for csv_warden.column_shifter."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_shifter import shift_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "data.csv"


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_offset_only(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"x": "10"}, {"x": "20"}, {"x": "30"}])
    r = shift_csv(str(tmp_csv), str(out), column="x", offset=5.0)
    rows = _read(out)
    assert [row["x"] for row in rows] == ["15", "25", "35"]
    assert r.rows_shifted == 3
    assert r.rows_skipped == 0


def test_scale_only(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"val": "2"}, {"val": "4"}, {"val": "6"}])
    r = shift_csv(str(tmp_csv), str(out), column="val", scale=3.0)
    rows = _read(out)
    assert [row["val"] for row in rows] == ["6", "12", "18"]
    assert r.rows_shifted == 3


def test_offset_and_scale(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"n": "1"}, {"n": "2"}])
    shift_csv(str(tmp_csv), str(out), column="n", offset=1.0, scale=2.0)
    rows = _read(out)
    assert rows[0]["n"] == "3"
    assert rows[1]["n"] == "5"


def test_suffix_creates_new_column(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"score": "100"}, {"score": "200"}])
    r = shift_csv(str(tmp_csv), str(out), column="score", offset=10.0, suffix="_shifted")
    rows = _read(out)
    assert "score" in rows[0]
    assert "score_shifted" in rows[0]
    assert rows[0]["score"] == "100"
    assert rows[0]["score_shifted"] == "110"
    assert r.rows_shifted == 2


def test_non_numeric_rows_skipped(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"v": "10"}, {"v": "n/a"}, {"v": "30"}])
    r = shift_csv(str(tmp_csv), str(out), column="v", offset=1.0)
    rows = _read(out)
    assert rows[0]["v"] == "11"
    assert rows[1]["v"] == "n/a"
    assert rows[2]["v"] == "31"
    assert r.rows_skipped == 1
    assert r.rows_shifted == 2


def test_missing_file_returns_error(tmp_path):
    r = shift_csv("/no/such/file.csv", str(tmp_path / "out.csv"), column="x")
    assert r.errors
    assert "not found" in r.errors[0].lower()


def test_missing_column_returns_error(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"a": "1"}])
    r = shift_csv(str(tmp_csv), str(out), column="z")
    assert any("not found" in e.lower() for e in r.errors)


def test_summary_contains_key_info(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    _write(tmp_csv, [{"x": "5"}])
    r = shift_csv(str(tmp_csv), str(out), column="x", offset=2.0)
    s = summary(r)
    assert "Rows shifted" in s
    assert "x" in s
