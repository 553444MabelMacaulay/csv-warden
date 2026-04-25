"""Tests for csv_warden.column_cumulator."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from csv_warden.column_cumulator import cumulate_csv, summary, SUPPORTED_OPS


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None) -> Path:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_cumsum_basic(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"val": "1"}, {"val": "2"}, {"val": "3"}])
    out = tmp_csv / "out.csv"
    result = cumulate_csv(str(src), str(out), column="val", op="sum")
    assert result.rows_processed == 3
    assert result.rows_skipped == 0
    rows = _read(out)
    assert [r["val_cum_sum"] for r in rows] == ["1.0", "3.0", "6.0"]


def test_cumproduct(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"x": "2"}, {"x": "3"}, {"x": "4"}])
    out = tmp_csv / "out.csv"
    result = cumulate_csv(str(src), str(out), column="x", op="product")
    rows = _read(out)
    assert rows[0]["x_cum_product"] == "2.0"
    assert rows[1]["x_cum_product"] == "6.0"
    assert rows[2]["x_cum_product"] == "24.0"


def test_cummin(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"v": "5"}, {"v": "3"}, {"v": "4"}])
    out = tmp_csv / "out.csv"
    cumulate_csv(str(src), str(out), column="v", op="min")
    rows = _read(out)
    assert [r["v_cum_min"] for r in rows] == ["5.0", "3.0", "3.0"]


def test_cummax(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"v": "1"}, {"v": "9"}, {"v": "4"}])
    out = tmp_csv / "out.csv"
    cumulate_csv(str(src), str(out), column="v", op="max")
    rows = _read(out)
    assert [r["v_cum_max"] for r in rows] == ["1.0", "9.0", "9.0"]


def test_custom_new_column_name(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"n": "10"}, {"n": "20"}])
    out = tmp_csv / "out.csv"
    cumulate_csv(str(src), str(out), column="n", op="sum", new_column="running_total")
    rows = _read(out)
    assert "running_total" in rows[0]
    assert rows[1]["running_total"] == "30.0"


def test_skips_non_numeric_rows(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"v": "1"}, {"v": "N/A"}, {"v": "3"}])
    out = tmp_csv / "out.csv"
    result = cumulate_csv(str(src), str(out), column="v", op="sum")
    assert result.rows_skipped == 1
    assert result.rows_processed == 2
    rows = _read(out)
    assert rows[1]["v_cum_sum"] == ""
    assert rows[2]["v_cum_sum"] == "4.0"


def test_missing_file(tmp_csv):
    result = cumulate_csv("/no/such/file.csv", str(tmp_csv / "out.csv"), column="v")
    assert result.errors
    assert "not found" in result.errors[0]


def test_column_not_found(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": "1"}])
    result = cumulate_csv(str(src), str(tmp_csv / "out.csv"), column="missing")
    assert any("not found" in e for e in result.errors)


def test_unsupported_op(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"v": "1"}])
    with pytest.raises(ValueError, match="Unsupported op"):
        cumulate_csv(str(src), str(tmp_csv / "out.csv"), column="v", op="mean")


def test_summary_output(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"v": "1"}, {"v": "2"}])
    out = tmp_csv / "out.csv"
    result = cumulate_csv(str(src), str(out), column="v", op="sum")
    s = summary(result)
    assert "v_cum_sum" in s
    assert "Rows processed" in s
