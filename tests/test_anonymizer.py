"""Tests for csv_warden.anonymizer."""
import csv
import pytest
from pathlib import Path
from csv_warden.anonymizer import anonymize_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_hash_column(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    result = anonymize_csv(str(src), str(out), columns=["name"])
    assert result.error is None
    assert result.rows_processed == 2
    rows = _read(out)
    assert rows[0]["name"] != "Alice"
    assert rows[0]["age"] == "30"


def test_mask_column(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"email": "a@b.com"}, {"email": "c@d.com"}])
    result = anonymize_csv(str(src), str(out), columns=["email"], mask=True)
    rows = _read(out)
    assert all(r["email"] == "***" for r in rows)


def test_column_not_found(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice"}])
    result = anonymize_csv(str(src), str(out), columns=["ssn"])
    assert "ssn" in result.columns_not_found


def test_file_not_found(tmp_csv):
    result = anonymize_csv("no.csv", str(tmp_csv / "out.csv"), columns=["x"])
    assert result.error is not None


def test_empty_value_hashed_as_empty(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": ""}])
    result = anonymize_csv(str(src), str(out), columns=["name"])
    rows = _read(out)
    assert rows[0]["name"] == ""


def test_summary_contains_rows(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice"}])
    result = anonymize_csv(str(src), str(out), columns=["name"])
    s = summary(result)
    assert "1" in s
    assert "name" in s
