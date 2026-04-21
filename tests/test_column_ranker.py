"""Tests for csv_warden.column_ranker."""
import csv
from pathlib import Path

import pytest

from csv_warden.column_ranker import rank_csv, summary, SUPPORTED_METHODS


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows:
        return
    fn = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_dense_rank_ascending(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "a", "score": "10"}, {"name": "b", "score": "20"}, {"name": "c", "score": "10"}])
    r = rank_csv(str(src), str(out), column="score", method="dense")
    rows = _read(out)
    ranks = {row["name"]: row["score_rank"] for row in rows}
    assert ranks["a"] == ranks["c"] == "1"
    assert ranks["b"] == "2"
    assert r.rows_ranked == 3
    assert r.rows_skipped == 0


def test_dense_rank_descending(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "5"}, {"v": "3"}, {"v": "5"}, {"v": "1"}])
    r = rank_csv(str(src), str(out), column="v", method="dense", ascending=False)
    rows = _read(out)
    assert rows[0]["v_rank"] == "1"  # 5 is highest
    assert rows[3]["v_rank"] == "3"  # 1 is lowest
    assert r.rows_ranked == 4


def test_min_rank(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "10"}, {"x": "10"}, {"x": "20"}])
    rank_csv(str(src), str(out), column="x", method="min")
    rows = _read(out)
    assert rows[0]["x_rank"] == rows[1]["x_rank"] == "1"
    assert rows[2]["x_rank"] == "3"


def test_percent_rank(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "1"}, {"v": "2"}, {"v": "3"}, {"v": "4"}])
    rank_csv(str(src), str(out), column="v", method="percent")
    rows = _read(out)
    assert float(rows[0]["v_rank"]) == pytest.approx(0.25)
    assert float(rows[3]["v_rank"]) == pytest.approx(1.0)


def test_custom_new_column_name(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "3"}, {"val": "1"}])
    rank_csv(str(src), str(out), column="val", new_column="position")
    rows = _read(out)
    assert "position" in rows[0]
    assert "val_rank" not in rows[0]


def test_skips_non_numeric_rows(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "10"}, {"v": "N/A"}, {"v": "5"}])
    r = rank_csv(str(src), str(out), column="v")
    assert r.rows_skipped == 1
    assert r.rows_ranked == 2
    rows = _read(out)
    assert rows[1]["v_rank"] == ""


def test_missing_file(tmp_csv):
    r = rank_csv(str(tmp_csv / "no.csv"), str(tmp_csv / "out.csv"), column="v")
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = rank_csv(str(src), str(out), column="z")
    assert any("not found" in e for e in r.errors)


def test_unsupported_method(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "1"}])
    r = rank_csv(str(src), str(out), column="v", method="bogus")
    assert any("Unsupported" in e for e in r.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "1"}, {"v": "2"}])
    r = rank_csv(str(src), str(out), column="v")
    s = summary(r)
    assert "Ranked" in s
    assert "dense" in s
