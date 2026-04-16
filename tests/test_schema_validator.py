"""Tests for csv_warden.schema_validator."""
import pytest
from pathlib import Path
from csv_warden.schema_validator import validate_schema


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "data.csv"


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8")


def test_valid_schema(tmp_csv):
    _write(tmp_csv, "name,age,score\nAlice,30,9.5\nBob,25,8.0\n")
    r = validate_schema(str(tmp_csv), {"age": "int", "score": "float"})
    assert r.valid
    assert r.rows_checked == 2


def test_invalid_int(tmp_csv):
    _write(tmp_csv, "name,age\nAlice,thirty\n")
    r = validate_schema(str(tmp_csv), {"age": "int"})
    assert not r.valid
    assert any("age" in e for e in r.errors)


def test_invalid_float(tmp_csv):
    _write(tmp_csv, "name,score\nAlice,abc\n")
    r = validate_schema(str(tmp_csv), {"score": "float"})
    assert not r.valid


def test_bool_valid(tmp_csv):
    _write(tmp_csv, "active\ntrue\n0\nFalse\n")
    r = validate_schema(str(tmp_csv), {"active": "bool"})
    assert r.valid


def test_bool_invalid(tmp_csv):
    _write(tmp_csv, "active\nyes\n")
    r = validate_schema(str(tmp_csv), {"active": "bool"})
    assert not r.valid


def test_required_column_missing_from_header(tmp_csv):
    _write(tmp_csv, "name,age\nAlice,30\n")
    r = validate_schema(str(tmp_csv), {}, required=["score"])
    assert not r.valid
    assert any("score" in e for e in r.errors)


def test_required_column_empty_value(tmp_csv):
    _write(tmp_csv, "name,age\nAlice,\n")
    r = validate_schema(str(tmp_csv), {"age": "int"}, required=["age"])
    assert not r.valid


def test_optional_empty_value_ok(tmp_csv):
    _write(tmp_csv, "name,age\nAlice,\n")
    r = validate_schema(str(tmp_csv), {"age": "int"})
    assert r.valid


def test_file_not_found():
    r = validate_schema("no_such_file.csv", {"x": "int"})
    assert not r.valid
    assert any("not found" in e for e in r.errors)


def test_unknown_type(tmp_csv):
    _write(tmp_csv, "x\n1\n")
    r = validate_schema(str(tmp_csv), {"x": "datetime"})
    assert not r.valid


def test_summary_contains_status(tmp_csv):
    _write(tmp_csv, "age\n5\n")
    r = validate_schema(str(tmp_csv), {"age": "int"})
    assert "PASS" in r.summary()
