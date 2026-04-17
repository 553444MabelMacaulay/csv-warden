"""Tests for csv_warden.column_caster."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_caster import cast_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_cast_to_int(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice", "age": "30.0"}, {"name": "bob", "age": "25.9"}], ["name", "age"])
    result = cast_csv(str(src), str(out), {"age": "int"})
    assert result.success
    rows = _read(out)
    assert rows[0]["age"] == "30"
    assert rows[1]["age"] == "25"


def test_cast_to_float(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "3"}], ["val"])
    result = cast_csv(str(src), str(out), {"val": "float"})
    assert result.success
    assert _read(out)[0]["val"] == "3.0"


def test_cast_to_bool(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"flag": "yes"}, {"flag": "no"}], ["flag"])
    result = cast_csv(str(src), str(out), {"flag": "bool"})
    assert result.success
    rows = _read(out)
    assert rows[0]["flag"] == "True"
    assert rows[1]["flag"] == "False"


def test_invalid_cast_value(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"age": "not_a_number"}], ["age"])
    result = cast_csv(str(src), str(out), {"age": "int"})
    assert not result.success
    assert any("age" in e for e in result.errors)


def test_unsupported_type(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"col": "val"}], ["col"])
    result = cast_csv(str(src), str(out), {"col": "datetime"})
    assert not result.success


def test_missing_file(tmp_csv):
    result = cast_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), {"x": "int"})
    assert not result.success
    assert "not found" in result.errors[0]


def test_unknown_column_is_ignored(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    result = cast_csv(str(src), str(out), {"z": "int"})
    assert result.success
    assert result.rows_processed == 1


def test_summary_contains_status(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"n": "5"}], ["n"])
    result = cast_csv(str(src), str(out), {"n": "float"})
    s = summary(result)
    assert "OK" in s
    assert "n→float" in s
