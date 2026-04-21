"""Tests for csv_warden.column_interpolator."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_interpolator import interpolate_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows):
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_linear_fills_interior_gap(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"x": "0"}, {"x": ""}, {"x": ""}, {"x": "6"},
    ])
    r = interpolate_csv(str(src), str(out), "x", method="linear")
    assert r.rows_filled == 2
    rows = _read(out)
    assert float(rows[1]["x"]) == pytest.approx(2.0)
    assert float(rows[2]["x"]) == pytest.approx(4.0)


def test_forward_fill(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [
        {"v": "10"}, {"v": ""}, {"v": ""}, {"v": "20"},
    ])
    r = interpolate_csv(str(src), str(out), "v", method="forward")
    assert r.rows_filled == 2
    rows = _read(out)
    assert rows[1]["v"] == "10.0"
    assert rows[2]["v"] == "10.0"


def test_no_gap_returns_zero_filled(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"n": "1"}, {"n": "2"}, {"n": "3"}])
    r = interpolate_csv(str(src), str(out), "n")
    assert r.rows_filled == 0


def test_missing_file(tmp_csv):
    r = interpolate_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), "x")
    assert r.errors
    assert "not found" in r.errors[0].lower()


def test_column_not_found(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = interpolate_csv(str(src), str(out), "z")
    assert any("not found" in e.lower() for e in r.errors)


def test_unknown_method(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = interpolate_csv(str(src), str(out), "a", method="spline")
    assert any("unknown method" in e.lower() for e in r.errors)


def test_leading_gap_not_filled_by_linear(tmp_csv):
    """Linear cannot extrapolate – leading Nones stay None."""
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": ""}, {"v": ""}, {"v": "4"}])
    r = interpolate_csv(str(src), str(out), "v", method="linear")
    rows = _read(out)
    assert rows[0]["v"] == ""
    assert rows[1]["v"] == ""
    assert r.rows_filled == 0


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"q": "1"}, {"q": ""}, {"q": "3"}])
    r = interpolate_csv(str(src), str(out), "q")
    s = summary(r)
    assert "q" in s
    assert "linear" in s
    assert "1" in s
