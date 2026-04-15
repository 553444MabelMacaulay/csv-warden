"""Tests for csv_warden.transformer."""

import csv
from pathlib import Path

import pytest

from csv_warden.transformer import transform_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]) -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def _read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_upper_transform(tmp_csv):
    src = _write(tmp_csv / "in.csv",
                 [{"name": "alice", "age": "30"}], ["name", "age"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"name": "upper"})
    assert result.rows_processed == 1
    assert result.errors == []
    rows = _read(out)
    assert rows[0]["name"] == "ALICE"
    assert rows[0]["age"] == "30"


def test_lower_transform(tmp_csv):
    src = _write(tmp_csv / "in.csv",
                 [{"email": "USER@EXAMPLE.COM"}], ["email"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"email": "lower"})
    assert result.errors == []
    assert _read(out)[0]["email"] == "user@example.com"


def test_multiple_columns(tmp_csv):
    src = _write(tmp_csv / "in.csv",
                 [{"first": "bob", "last": "SMITH", "id": "1"}],
                 ["first", "last", "id"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"first": "upper", "last": "lower"})
    assert result.columns_transformed == ["first", "last"]
    row = _read(out)[0]
    assert row["first"] == "BOB"
    assert row["last"] == "smith"
    assert row["id"] == "1"


def test_file_not_found(tmp_csv):
    result = transform_csv("no_such_file.csv", str(tmp_csv / "out.csv"), {})
    assert any("not found" in e for e in result.errors)


def test_unknown_transform(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"col": "val"}], ["col"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"col": "reverse"})
    assert any("Unknown transform" in e for e in result.errors)


def test_missing_column(tmp_csv):
    src = _write(tmp_csv / "in.csv", [{"col": "val"}], ["col"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"nonexistent": "upper"})
    assert any("not found" in e for e in result.errors)


def test_summary_contains_key_info(tmp_csv):
    src = _write(tmp_csv / "in.csv",
                 [{"city": "london"}], ["city"])
    out = str(tmp_csv / "out.csv")
    result = transform_csv(src, out, {"city": "title"})
    s = summary(result)
    assert "Rows processed" in s
    assert "city" in s
