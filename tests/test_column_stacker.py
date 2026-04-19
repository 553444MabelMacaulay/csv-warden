"""Tests for csv_warden.column_stacker."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_stacker import stack_csv, summary


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


def test_basic_stack(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "jan": "10", "feb": "20"}, {"id": "2", "jan": "30", "feb": "40"}], ["id", "jan", "feb"])
    result = stack_csv(str(src), str(out), columns=["jan", "feb"], id_columns=["id"])
    assert result.rows_in == 2
    assert result.rows_out == 4
    rows = _read(out)
    assert len(rows) == 4
    keys = [r["key"] for r in rows]
    assert keys == ["jan", "feb", "jan", "feb"]


def test_values_correct(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "A", "x": "1", "y": "2"}], ["id", "x", "y"])
    stack_csv(str(src), str(out), columns=["x", "y"], id_columns=["id"])
    rows = _read(out)
    assert rows[0]["value"] == "1"
    assert rows[1]["value"] == "2"


def test_custom_key_value_col_names(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "a": "v"}], ["id", "a"])
    stack_csv(str(src), str(out), columns=["a"], id_columns=["id"], key_col="metric", value_col="amount")
    rows = _read(out)
    assert "metric" in rows[0]
    assert "amount" in rows[0]


def test_missing_file(tmp_csv):
    result = stack_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), columns=["a"])
    assert result.errors
    assert "not found" in result.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "a": "2"}], ["id", "a"])
    result = stack_csv(str(src), str(out), columns=["b"], id_columns=["id"])
    assert result.errors
    assert "b" in result.errors[0]


def test_id_columns_inferred(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "jan": "5", "feb": "6"}], ["id", "jan", "feb"])
    result = stack_csv(str(src), str(out), columns=["jan", "feb"])
    rows = _read(out)
    assert "id" in rows[0]
    assert result.rows_out == 2


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"id": "1", "a": "x"}], ["id", "a"])
    result = stack_csv(str(src), str(out), columns=["a"], id_columns=["id"])
    s = summary(result)
    assert "Columns stacked" in s
    assert "a" in s
