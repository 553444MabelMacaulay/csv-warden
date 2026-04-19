"""Tests for csv_warden.column_encoder (one-hot encoding)."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_encoder import onehot_encode_csv, summary


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


def test_basic_onehot(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "a", "color": "red"}, {"name": "b", "color": "blue"}, {"name": "c", "color": "red"}], ["name", "color"])
    result = onehot_encode_csv(str(src), str(out), column="color")
    assert result.success()
    assert result.rows_processed == 3
    assert "color_blue" in result.new_columns
    assert "color_red" in result.new_columns
    rows = _read(out)
    assert rows[0]["color_red"] == "1"
    assert rows[0]["color_blue"] == "0"
    assert rows[1]["color_blue"] == "1"


def test_drop_original(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1", "cat": "a"}, {"x": "2", "cat": "b"}], ["x", "cat"])
    result = onehot_encode_csv(str(src), str(out), column="cat", drop_original=True)
    assert result.success()
    rows = _read(out)
    assert "cat" not in rows[0]
    assert "cat_a" in rows[0]


def test_custom_prefix(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "yes"}, {"v": "no"}], ["v"])
    result = onehot_encode_csv(str(src), str(out), column="v", prefix="flag")
    assert "flag_yes" in result.new_columns
    assert "flag_no" in result.new_columns


def test_missing_file(tmp_csv):
    result = onehot_encode_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), column="x")
    assert not result.success()
    assert "not found" in result.error


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    result = onehot_encode_csv(str(src), str(out), column="z")
    assert not result.success()
    assert "z" in result.error


def test_summary_success(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"col": "x"}, {"col": "y"}], ["col"])
    result = onehot_encode_csv(str(src), str(out), column="col")
    s = summary(result)
    assert "One-hot" in s
    assert "col" in s


def test_summary_error(tmp_csv):
    result = onehot_encode_csv(str(tmp_csv / "x.csv"), str(tmp_csv / "o.csv"), column="c")
    s = summary(result)
    assert "ERROR" in s
