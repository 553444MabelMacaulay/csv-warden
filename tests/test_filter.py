"""Tests for csv_warden.filter."""
import csv
import io
from pathlib import Path

import pytest

from csv_warden.filter import filter_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]) -> str:
    p = path / "input.csv"
    with p.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(p)


def test_keep_matching_rows(tmp_csv):
    src = _write(
        tmp_csv,
        [{"name": "alice", "role": "admin"}, {"name": "bob", "role": "user"}],
        ["name", "role"],
    )
    out = str(tmp_csv / "out.csv")
    result = filter_csv(src, out, column="role", value="admin")
    assert result.kept_rows == 1
    assert result.dropped_rows == 1
    assert result.total_rows == 2
    assert not result.errors


def test_exclude_matching_rows(tmp_csv):
    src = _write(
        tmp_csv,
        [{"name": "alice", "role": "admin"}, {"name": "bob", "role": "user"}],
        ["name", "role"],
    )
    out = str(tmp_csv / "out.csv")
    result = filter_csv(src, out, column="role", value="admin", exclude=True)
    assert result.kept_rows == 1
    assert result.dropped_rows == 1


def test_output_file_written(tmp_csv):
    src = _write(
        tmp_csv,
        [{"city": "London", "pop": "9"}, {"city": "Paris", "pop": "2"}],
        ["city", "pop"],
    )
    out = str(tmp_csv / "filtered.csv")
    filter_csv(src, out, column="city", value="London")
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 1
    assert rows[0]["city"] == "London"


def test_missing_file_returns_error(tmp_csv):
    result = filter_csv(str(tmp_csv / "nope.csv"), column="x", value="1")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_missing_column_returns_error(tmp_csv):
    src = _write(tmp_csv, [{"a": "1"}], ["a"])
    result = filter_csv(src, column="z", value="1")
    assert result.errors
    assert "Column 'z'" in result.errors[0]


def test_no_column_arg_returns_error(tmp_csv):
    src = _write(tmp_csv, [{"a": "1"}], ["a"])
    result = filter_csv(src)
    assert result.errors


def test_summary_contains_key_fields(tmp_csv):
    src = _write(tmp_csv, [{"x": "1"}], ["x"])
    result = filter_csv(src, column="x", value="1")
    s = summary(result)
    assert "Kept rows" in s
    assert "Dropped rows" in s
