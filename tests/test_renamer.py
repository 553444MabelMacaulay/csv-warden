"""Tests for csv_warden.renamer."""
import csv
import os
import pytest
from pathlib import Path

from csv_warden.renamer import rename_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[list[str]]) -> str:
    p = str(path)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return p


def _read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_rename_single_column(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["name", "age"], ["Alice", "30"], ["Bob", "25"]])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {"name": "full_name"})
    assert result.errors == []
    assert result.renamed == {"name": "full_name"}
    assert result.rows_written == 2
    rows = _read(out)
    assert rows[0]["full_name"] == "Alice"
    assert "name" not in rows[0]


def test_rename_multiple_columns(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["a", "b", "c"], ["1", "2", "3"]])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {"a": "alpha", "c": "gamma"})
    assert result.errors == []
    assert set(result.renamed.keys()) == {"a", "c"}
    rows = _read(out)
    assert "alpha" in rows[0]
    assert "gamma" in rows[0]
    assert "b" in rows[0]


def test_skips_unknown_column(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["x", "y"], ["1", "2"]])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {"z": "zeta"})
    assert "z" in result.skipped
    assert result.errors == []
    rows = _read(out)
    assert list(rows[0].keys()) == ["x", "y"]


def test_file_not_found(tmp_csv):
    result = rename_csv("nonexistent.csv", str(tmp_csv / "out.csv"), {"a": "b"})
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_empty_file(tmp_csv):
    src = _write(tmp_csv / "in.csv", [])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {"a": "b"})
    assert result.errors


def test_summary_contains_renamed(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["id", "val"], ["1", "foo"]])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {"id": "identifier"})
    s = summary(result)
    assert "identifier" in s
    assert "id" in s


def test_no_mapping_preserves_headers(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["p", "q"], ["10", "20"]])
    out = str(tmp_csv / "out.csv")
    result = rename_csv(src, out, {})
    assert result.errors == []
    rows = _read(out)
    assert list(rows[0].keys()) == ["p", "q"]
