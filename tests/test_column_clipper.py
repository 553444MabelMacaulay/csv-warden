"""Tests for csv_warden.column_clipper."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_clipper import clip_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_clip_low(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "-5"}, {"val": "3"}, {"val": "10"}], ["val"])
    r = clip_csv(str(src), str(out), "val", low=0)
    assert r.rows_clipped == 1
    rows = _read(out)
    assert rows[0]["val"] == "0"
    assert rows[1]["val"] == "3"
    assert rows[2]["val"] == "10"


def test_clip_high(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "1"}, {"val": "50"}, {"val": "100"}], ["val"])
    r = clip_csv(str(src), str(out), "val", high=20)
    assert r.rows_clipped == 2
    rows = _read(out)
    assert rows[1]["val"] == "20"
    assert rows[2]["val"] == "20"


def test_clip_both_bounds(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "-1"}, {"x": "5"}, {"x": "99"}], ["x"])
    r = clip_csv(str(src), str(out), "x", low=0, high=10)
    assert r.rows_clipped == 2


def test_non_numeric_skipped(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "abc"}, {"v": "5"}], ["v"])
    r = clip_csv(str(src), str(out), "v", low=0, high=10)
    assert r.rows_skipped == 1
    assert r.rows_clipped == 0


def test_missing_file(tmp_csv):
    r = clip_csv(str(tmp_csv / "no.csv"), str(tmp_csv / "out.csv"), "v", low=0)
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    r = clip_csv(str(src), str(out), "z", low=0)
    assert any("not found" in e for e in r.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"n": "3"}], ["n"])
    r = clip_csv(str(src), str(out), "n", low=0, high=5)
    s = summary(r)
    assert "Clipped" in s
    assert "n" in s
