import csv
import pytest
from pathlib import Path
from csv_warden.column_duplicator import duplicate_columns, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_duplicate_single_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    result = duplicate_columns(str(src), str(out), {"name": "name_copy"})
    assert not result.errors
    assert "name->name_copy" in result.duplicated
    rows = _read(out)
    assert rows[0]["name_copy"] == "Alice"
    assert rows[1]["name_copy"] == "Bob"


def test_duplicate_preserves_original(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1", "y": "2"}])
    duplicate_columns(str(src), str(out), {"x": "x2"})
    rows = _read(out)
    assert rows[0]["x"] == "1"
    assert rows[0]["x2"] == "1"
    assert rows[0]["y"] == "2"


def test_duplicate_multiple_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = duplicate_columns(str(src), str(out), {"a": "a_dup", "b": "b_dup"})
    assert len(result.duplicated) == 2
    rows = _read(out)
    assert rows[0]["a_dup"] == "1"
    assert rows[0]["b_dup"] == "2"


def test_missing_source_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = duplicate_columns(str(src), str(out), {"z": "z_dup"})
    assert any("z" in e for e in result.errors)
    assert not result.duplicated


def test_target_column_already_exists(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = duplicate_columns(str(src), str(out), {"a": "b"})
    assert any("already exists" in e for e in result.errors)


def test_file_not_found(tmp_csv):
    out = tmp_csv / "out.csv"
    result = duplicate_columns("no_such.csv", str(out), {"a": "a2"})
    assert result.errors


def test_summary_contains_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"col": "val"}])
    result = duplicate_columns(str(src), str(out), {"col": "col2"})
    s = summary(result)
    assert "col->col2" in s
