"""Tests for csv_warden.column_concatenator."""
import csv
from pathlib import Path

import pytest

from csv_warden.column_concatenator import concatenate_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    fn = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_basic_concat(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"first": "John", "last": "Doe"}])
    result = concatenate_csv(str(src), str(dst), ["first", "last"], new_column="full")
    assert result.success
    rows = _read(dst)
    assert rows[0]["full"] == "John Doe"


def test_custom_separator(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"a": "foo", "b": "bar"}])
    result = concatenate_csv(str(src), str(dst), ["a", "b"], separator="-")
    assert result.success
    rows = _read(dst)
    assert rows[0]["concatenated"] == "foo-bar"


def test_original_columns_preserved(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"x": "1", "y": "2", "z": "3"}])
    concatenate_csv(str(src), str(dst), ["x", "y"])
    rows = _read(dst)
    assert "x" in rows[0]
    assert "y" in rows[0]
    assert "z" in rows[0]


def test_drop_sources(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"first": "Alice", "last": "Smith", "age": "30"}])
    result = concatenate_csv(
        str(src), str(dst), ["first", "last"], new_column="name", drop_sources=True
    )
    assert result.success
    rows = _read(dst)
    assert "first" not in rows[0]
    assert "last" not in rows[0]
    assert rows[0]["name"] == "Alice Smith"
    assert rows[0]["age"] == "30"


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = concatenate_csv(str(src), str(dst), ["a", "nonexistent"])
    assert not result.success
    assert "nonexistent" in result.missing_columns


def test_missing_file_returns_error(tmp_csv):
    result = concatenate_csv(
        str(tmp_csv / "ghost.csv"), str(tmp_csv / "out.csv"), ["a"]
    )
    assert not result.success
    assert "not found" in result.error.lower()


def test_rows_written_count(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"a": str(i), "b": str(i * 2)} for i in range(5)])
    result = concatenate_csv(str(src), str(dst), ["a", "b"])
    assert result.rows_written == 5


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    dst = tmp_csv / "out.csv"
    _write(src, [{"p": "hello", "q": "world"}])
    result = concatenate_csv(str(src), str(dst), ["p", "q"], new_column="pq", separator="|")
    s = summary(result)
    assert "pq" in s
    assert "'|'" in s
    assert "1" in s
