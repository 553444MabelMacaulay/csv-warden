import csv
import pytest
from pathlib import Path
from csv_warden.column_binner import bin_csv


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(rows, headers):
        p = tmp_path / "input.csv"
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_missing_file(tmp_path):
    result = bin_csv(str(tmp_path / "nope.csv"), str(tmp_path / "out.csv"), "val")
    assert result.errors
    assert "not found" in result.errors[0]


def test_column_not_found(tmp_csv, tmp_path):
    p = tmp_csv([{"a": "1"}], ["a"])
    result = bin_csv(p, str(tmp_path / "out.csv"), "missing")
    assert any("not found" in e for e in result.errors)


def test_basic_bin(tmp_csv, tmp_path):
    rows = [{"score": str(i)} for i in range(10)]
    p = tmp_csv(rows, ["score"])
    out = str(tmp_path / "out.csv")
    result = bin_csv(p, out, "score", bins=2)
    assert result.rows_processed == 10
    assert result.rows_binned == 10
    assert not result.errors
    data = _read(out)
    assert "score_bin" in data[0]
    bins_seen = {r["score_bin"] for r in data}
    assert len(bins_seen) == 2


def test_custom_new_column(tmp_csv, tmp_path):
    rows = [{"val": str(i)} for i in range(5)]
    p = tmp_csv(rows, ["val"])
    out = str(tmp_path / "out.csv")
    bin_csv(p, out, "val", bins=5, new_column="bucket")
    data = _read(out)
    assert "bucket" in data[0]


def test_custom_labels(tmp_csv, tmp_path):
    rows = [{"x": str(i)} for i in range(6)]
    p = tmp_csv(rows, ["x"])
    out = str(tmp_path / "out.csv")
    result = bin_csv(p, out, "x", bins=3, labels=["low", "mid", "high"])
    data = _read(out)
    labels_seen = {r["x_bin"] for r in data}
    assert labels_seen <= {"low", "mid", "high"}


def test_non_numeric_skipped(tmp_csv, tmp_path):
    rows = [{"v": "1"}, {"v": "abc"}, {"v": "3"}]
    p = tmp_csv(rows, ["v"])
    out = str(tmp_path / "out.csv")
    result = bin_csv(p, out, "v", bins=2)
    assert result.rows_binned == 2
    data = _read(out)
    assert data[1]["v_bin"] == ""


def test_summary_output(tmp_csv, tmp_path):
    rows = [{"n": str(i)} for i in range(4)]
    p = tmp_csv(rows, ["n"])
    out = str(tmp_path / "out.csv")
    result = bin_csv(p, out, "n", bins=2)
    s = result.summary()
    assert "Rows binned" in s
    assert "4" in s
