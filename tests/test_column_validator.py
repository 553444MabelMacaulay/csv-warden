"""Tests for csv_warden.column_validator."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_validator import validate_columns, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "data.csv"


def _write(path: Path, rows: list[dict], fieldnames=None):
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_valid_pattern(tmp_csv):
    _write(tmp_csv, [{"code": "A1"}, {"code": "B2"}, {"code": "C9"}])
    result = validate_columns(str(tmp_csv), patterns={"code": r"[A-Z]\d"})
    assert result.success
    assert result.total_rows == 3
    assert result.invalid_rows == 0


def test_invalid_pattern(tmp_csv):
    _write(tmp_csv, [{"code": "A1"}, {"code": "bad"}, {"code": "C9"}])
    result = validate_columns(str(tmp_csv), patterns={"code": r"[A-Z]\d"})
    assert not result.success
    assert result.invalid_rows == 1
    assert "'code'" in result.errors[0]


def test_allowed_values_pass(tmp_csv):
    _write(tmp_csv, [{"status": "active"}, {"status": "inactive"}])
    result = validate_columns(str(tmp_csv), allowed={"status": ["active", "inactive"]})
    assert result.success
    assert result.invalid_rows == 0


def test_allowed_values_fail(tmp_csv):
    _write(tmp_csv, [{"status": "active"}, {"status": "unknown"}])
    result = validate_columns(str(tmp_csv), allowed={"status": ["active", "inactive"]})
    assert not result.success
    assert result.invalid_rows == 1


def test_combined_pattern_and_allowed(tmp_csv):
    _write(tmp_csv, [{"code": "A1", "status": "active"}, {"code": "bad", "status": "nope"}])
    result = validate_columns(
        str(tmp_csv),
        patterns={"code": r"[A-Z]\d"},
        allowed={"status": ["active", "inactive"]},
    )
    assert not result.success
    assert result.invalid_rows == 1
    assert len(result.errors) == 2


def test_missing_file():
    result = validate_columns("nonexistent.csv")
    assert not result.success
    assert "not found" in result.errors[0]


def test_summary_pass(tmp_csv):
    _write(tmp_csv, [{"x": "1"}])
    result = validate_columns(str(tmp_csv))
    out = summary(result)
    assert "PASS" in out


def test_summary_fail(tmp_csv):
    _write(tmp_csv, [{"code": "bad"}])
    result = validate_columns(str(tmp_csv), patterns={"code": r"[A-Z]\d"})
    out = summary(result)
    assert "FAIL" in out
    assert "Errors" in out
