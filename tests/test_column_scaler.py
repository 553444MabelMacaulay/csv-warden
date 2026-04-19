"""Tests for csv_warden.column_scaler."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_scaler import scale_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_minmax_scale(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "0"}, {"val": "5"}, {"val": "10"}], ["val"])
    r = scale_csv(str(src), str(out), "val", method="minmax")
    rows = _read(out)
    assert float(rows[0]["val"]) == pytest.approx(0.0)
    assert float(rows[1]["val"]) == pytest.approx(0.5)
    assert float(rows[2]["val"]) == pytest.approx(1.0)
    assert r.rows_scaled == 3
    assert r.rows_skipped == 0


def test_zscore_scale(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "2"}, {"val": "4"}, {"val": "6"}], ["val"])
    r = scale_csv(str(src), str(out), "val", method="zscore")
    rows = _read(out)
    assert float(rows[1]["val"]) == pytest.approx(0.0)
    assert r.rows_scaled == 3


def test_skips_non_numeric(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "1"}, {"val": "N/A"}, {"val": "3"}], ["val"])
    r = scale_csv(str(src), str(out), "val", method="minmax")
    assert r.rows_scaled == 2
    assert r.rows_skipped == 1
    rows = _read(out)
    assert rows[1]["val"] == "N/A"


def test_missing_file(tmp_csv):
    r = scale_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), "val")
    assert any("not found" in e for e in r.errors)


def test_unknown_method(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [{"val": "1"}], ["val"])
    r = scale_csv(str(src), str(tmp_csv / "out.csv"), "val", method="bad")
    assert any("Unknown method" in e for e in r.errors)


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "1"}], ["val"])
    r = scale_csv(str(src), str(out), "missing_col")
    assert any("not found" in e for e in r.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "1"}, {"val": "2"}], ["val"])
    r = scale_csv(str(src), str(out), "val", method="minmax")
    s = summary(r)
    assert "minmax" in s
    assert "val" in s
    assert "2" in s
