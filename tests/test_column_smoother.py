"""Tests for csv_warden.column_smoother."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_smoother import smooth_csv, summary


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


def test_missing_file(tmp_csv):
    r = smooth_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), "val")
    assert r.errors
    assert "not found" in r.errors[0].lower()


def test_column_not_found(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, [{"x": "1"}], ["x"])
    r = smooth_csv(str(src), str(tmp_csv / "out.csv"), "missing_col")
    assert r.errors
    assert "missing_col" in r.errors[0]


def test_unknown_method(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, [{"v": "1"}, {"v": "2"}], ["v"])
    r = smooth_csv(str(src), str(tmp_csv / "out.csv"), "v", method="median")
    assert r.errors
    assert "Unknown method" in r.errors[0]


def test_mean_smooth_basic(tmp_csv):
    src = tmp_csv / "data.csv"
    rows = [{"v": str(x)} for x in [1, 3, 5, 7, 9]]
    _write(src, rows, ["v"])
    out = tmp_csv / "out.csv"
    r = smooth_csv(str(src), str(out), "v", window=1, method="mean")
    assert r.rows_smoothed == 5
    assert r.rows_skipped == 0
    result = _read(out)
    # middle value 5 should be average of 3,5,7 = 5.0
    assert float(result[2]["v"]) == pytest.approx(5.0)


def test_mean_smooth_edges(tmp_csv):
    """Edge rows use a smaller window."""
    src = tmp_csv / "data.csv"
    rows = [{"v": str(x)} for x in [10, 20, 30]]
    _write(src, rows, ["v"])
    out = tmp_csv / "out.csv"
    smooth_csv(str(src), str(out), "v", window=1, method="mean")
    result = _read(out)
    # first row: average of 10, 20 = 15
    assert float(result[0]["v"]) == pytest.approx(15.0)
    # last row: average of 20, 30 = 25
    assert float(result[2]["v"]) == pytest.approx(25.0)


def test_gaussian_smooth(tmp_csv):
    src = tmp_csv / "data.csv"
    rows = [{"v": str(x)} for x in [0, 0, 100, 0, 0]]
    _write(src, rows, ["v"])
    out = tmp_csv / "out.csv"
    r = smooth_csv(str(src), str(out), "v", window=2, method="gaussian")
    assert r.rows_smoothed == 5
    result = _read(out)
    # peak should be at index 2 and smoothed value < 100
    peak = float(result[2]["v"])
    assert peak < 100.0
    assert peak > 0.0


def test_skips_non_numeric(tmp_csv):
    src = tmp_csv / "data.csv"
    rows = [{"v": "1"}, {"v": "N/A"}, {"v": "3"}]
    _write(src, rows, ["v"])
    out = tmp_csv / "out.csv"
    r = smooth_csv(str(src), str(out), "v", window=1)
    assert r.rows_skipped == 1
    assert r.rows_smoothed == 2


def test_other_columns_preserved(tmp_csv):
    src = tmp_csv / "data.csv"
    rows = [{"id": "a", "v": "1"}, {"id": "b", "v": "3"}, {"id": "c", "v": "5"}]
    _write(src, rows, ["id", "v"])
    out = tmp_csv / "out.csv"
    smooth_csv(str(src), str(out), "v", window=1)
    result = _read(out)
    assert [row["id"] for row in result] == ["a", "b", "c"]


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, [{"v": "1"}, {"v": "2"}], ["v"])
    out = tmp_csv / "out.csv"
    r = smooth_csv(str(src), str(out), "v", window=1, method="gaussian")
    s = summary(r)
    assert "gaussian" in s
    assert "v" in s
    assert "Smoothed rows" in s
