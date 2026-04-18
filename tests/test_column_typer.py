"""Tests for csv_warden.column_typer."""
import pytest
from pathlib import Path
from csv_warden.column_typer import infer_types, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "data.csv"


def _write(p: Path, rows: list[str]):
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_infer_int(tmp_csv):
    _write(tmp_csv, ["age", "10", "20", "30"])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "int"


def test_infer_float(tmp_csv):
    _write(tmp_csv, ["score", "1.5", "2.3", "0.0"])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "float"


def test_infer_bool(tmp_csv):
    _write(tmp_csv, ["active", "true", "false", "true"])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "bool"


def test_infer_date(tmp_csv):
    _write(tmp_csv, ["dob", "2000-01-01", "1999-12-31"])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "date"


def test_infer_string(tmp_csv):
    _write(tmp_csv, ["name", "Alice", "Bob"])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "string"


def test_multiple_columns(tmp_csv):
    _write(tmp_csv, ["name,age,score", "Alice,30,9.5", "Bob,25,8.0"])
    r = infer_types(str(tmp_csv))
    types = {c.name: c.inferred_type for c in r.columns}
    assert types["name"] == "string"
    assert types["age"] == "int"
    assert types["score"] == "float"


def test_missing_file():
    r = infer_types("nonexistent.csv")
    assert r.errors
    assert "not found" in r.errors[0]


def test_empty_column_defaults_to_string(tmp_csv):
    _write(tmp_csv, ["x", "", ""])
    r = infer_types(str(tmp_csv))
    assert r.columns[0].inferred_type == "string"


def test_summary_contains_column_names(tmp_csv):
    _write(tmp_csv, ["id,label", "1,foo", "2,bar"])
    r = infer_types(str(tmp_csv))
    s = summary(r)
    assert "id" in s
    assert "label" in s
