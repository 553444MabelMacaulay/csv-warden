"""Unit tests for csv_warden.column_regex_extractor."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from csv_warden.column_regex_extractor import regex_extract_csv


@pytest.fixture()
def tmp_csv(tmp_path: Path):
    return tmp_path


def _write(path: Path, rows: list[list[str]]) -> str:
    p = str(path)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return p


def _read(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_extract_named_groups(tmp_csv):
    src = _write(tmp_csv / "in.csv", [
        ["id", "date"],
        ["1", "2024-03-15"],
        ["2", "1999-12-01"],
    ])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="date",
                                pattern=r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")
    assert result.errors == []
    assert result.rows_total == 2
    assert result.rows_matched == 2
    assert set(result.new_columns) == {"year", "month", "day"}
    rows = _read(out)
    assert rows[0]["year"] == "2024"
    assert rows[0]["month"] == "03"
    assert rows[1]["day"] == "01"


def test_no_match_uses_fill_value(tmp_csv):
    src = _write(tmp_csv / "in.csv", [
        ["id", "code"],
        ["1", "ABC-123"],
        ["2", "no-match-here"],
    ])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="code",
                                pattern=r"(?P<num>\d{3})",
                                fill_value="N/A")
    assert result.errors == []
    rows = _read(out)
    assert rows[0]["num"] == "123"
    assert rows[1]["num"] == "N/A"


def test_drop_original(tmp_csv):
    src = _write(tmp_csv / "in.csv", [
        ["id", "email"],
        ["1", "user@example.com"],
    ])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="email",
                                pattern=r"(?P<user>[^@]+)@(?P<domain>.+)",
                                drop_original=True)
    assert result.errors == []
    rows = _read(out)
    assert "email" not in rows[0]
    assert rows[0]["user"] == "user"
    assert rows[0]["domain"] == "example.com"


def test_missing_file(tmp_csv):
    result = regex_extract_csv("/no/such/file.csv", str(tmp_csv / "out.csv"),
                                column="x", pattern=r"(?P<a>\d+)")
    assert any("not found" in e for e in result.errors)


def test_column_not_found(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["a", "b"], ["1", "2"]])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="z", pattern=r"(?P<x>\d+)")
    assert any("not found" in e for e in result.errors)


def test_pattern_without_named_groups(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["a"], ["hello"]])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="a", pattern=r"(\d+)")
    assert any("named" in e for e in result.errors)


def test_invalid_pattern(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["a"], ["hello"]])
    out = str(tmp_csv / "out.csv")
    result = regex_extract_csv(src, out, column="a", pattern=r"(?P<x>[")
    assert any("Invalid regex" in e for e in result.errors)
