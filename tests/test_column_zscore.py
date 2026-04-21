"""Tests for csv_warden.column_zscore."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

from csv_warden.column_zscore import zscore_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(tmp_csv / "nope.csv"), str(out), column="val")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_column_not_found(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"a": "1"}], ["a"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="missing")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_zscore_basic(tmp_csv):
    rows = [{"val": "2"}, {"val": "4"}, {"val": "6"}]
    src = _write(tmp_csv / "in.csv", rows, ["val"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="val")

    assert not result.errors
    assert result.rows_processed == 3
    assert result.rows_skipped == 0
    assert result.mean == pytest.approx(4.0)
    assert result.std == pytest.approx(math.sqrt(8 / 3))

    data = _read(out)
    assert "val_zscore" in data[0]
    z_middle = float(data[1]["val_zscore"])
    assert z_middle == pytest.approx(0.0, abs=1e-5)


def test_zscore_custom_new_column(tmp_csv):
    rows = [{"x": "10"}, {"x": "20"}, {"x": "30"}]
    src = _write(tmp_csv / "in.csv", rows, ["x"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="x", new_column="x_z")

    assert not result.errors
    data = _read(out)
    assert "x_z" in data[0]
    assert "x_zscore" not in data[0]


def test_zscore_skips_non_numeric(tmp_csv):
    rows = [{"v": "1"}, {"v": "abc"}, {"v": "3"}]
    src = _write(tmp_csv / "in.csv", rows, ["v"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="v")

    assert not result.errors
    assert result.rows_processed == 2
    assert result.rows_skipped == 1
    data = _read(out)
    assert data[1]["v_zscore"] == ""


def test_zscore_constant_column(tmp_csv):
    """All values identical -> std=0, z-score should be 0.0 for all."""
    rows = [{"c": "5"}, {"c": "5"}, {"c": "5"}]
    src = _write(tmp_csv / "in.csv", rows, ["c"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="c")

    assert not result.errors
    data = _read(out)
    for row in data:
        assert float(row["c_zscore"]) == pytest.approx(0.0)


def test_summary_output(tmp_csv):
    rows = [{"n": "1"}, {"n": "2"}, {"n": "3"}]
    src = _write(tmp_csv / "in.csv", rows, ["n"])
    out = tmp_csv / "out.csv"
    result = zscore_csv(str(src), str(out), column="n")
    s = summary(result)
    assert "Z-Score" in s
    assert "Mean" in s
    assert "Std Dev" in s
    assert "Processed" in s
