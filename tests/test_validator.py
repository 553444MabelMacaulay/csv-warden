"""Unit tests for csv_warden.validator."""

import textwrap
from pathlib import Path

import pytest

from csv_warden.validator import validate_csv


@pytest.fixture()
def tmp_csv(tmp_path):
    """Helper that writes content to a temp CSV and returns its path."""

    def _write(content: str) -> str:
        p: Path = tmp_path / "test.csv"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return str(p)

    return _write


def test_valid_csv(tmp_csv):
    path = tmp_csv("""\
        id,name,email
        1,Alice,alice@example.com
        2,Bob,bob@example.com
    """)
    result = validate_csv(path)
    assert result.is_valid
    assert result.row_count == 2
    assert result.column_count == 3
    assert result.errors == []


def test_file_not_found():
    result = validate_csv("nonexistent.csv")
    assert not result.is_valid
    assert any("not found" in e for e in result.errors)


def test_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    result = validate_csv(str(p))
    assert not result.is_valid
    assert any("empty" in e for e in result.errors)


def test_missing_required_headers(tmp_csv):
    path = tmp_csv("""\
        id,name
        1,Alice
    """)
    result = validate_csv(path, required_headers=["id", "name", "email"])
    assert not result.is_valid
    assert any("email" in e for e in result.errors)


def test_wrong_column_count(tmp_csv):
    path = tmp_csv("""\
        id,name,email
        1,Alice,alice@example.com
    """)
    result = validate_csv(path, expected_columns=2)
    assert not result.is_valid
    assert any("Expected 2" in e for e in result.errors)


def test_ragged_rows_produce_warnings(tmp_csv):
    path = tmp_csv("""\
        id,name,email
        1,Alice
        2,Bob,bob@example.com
    """)
    result = validate_csv(path)
    assert result.is_valid  # warnings do not flip is_valid
    assert len(result.warnings) == 1
    assert "Row 2" in result.warnings[0]


def test_custom_delimiter(tmp_csv):
    path = tmp_csv("""\
        id;name;email
        1;Alice;alice@example.com
    """)
    result = validate_csv(path, delimiter=";")
    assert result.is_valid
    assert result.column_count == 3
