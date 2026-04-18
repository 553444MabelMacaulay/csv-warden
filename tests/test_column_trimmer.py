"""Tests for csv_warden.column_trimmer."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_trimmer import trim_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_trim_basic(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alexander", "age": "30"}], ["name", "age"])
    result = trim_csv(str(src), str(out), {"name": 4})
    rows = _read(out)
    assert rows[0]["name"] == "Alex"
    assert result.cells_trimmed == 1
    assert result.rows_processed == 1


def test_no_trim_when_within_limit(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Jo", "age": "25"}], ["name", "age"])
    result = trim_csv(str(src), str(out), {"name": 10})
    rows = _read(out)
    assert rows[0]["name"] == "Jo"
    assert result.cells_trimmed == 0


def test_trim_with_ellipsis(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"desc": "Hello World", "id": "1"}], ["desc", "id"])
    result = trim_csv(str(src), str(out), {"desc": 8}, ellipsis_str="...")
    rows = _read(out)
    assert rows[0]["desc"] == "Hello..."
    assert len(rows[0]["desc"]) == 8
    assert result.cells_trimmed == 1


def test_trim_multiple_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(
        src,
        [{"a": "toolong", "b": "alsolong", "c": "ok"}],
        ["a", "b", "c"],
    )
    result = trim_csv(str(src), str(out), {"a": 3, "b": 4})
    rows = _read(out)
    assert rows[0]["a"] == "too"
    assert rows[0]["b"] == "also"
    assert rows[0]["c"] == "ok"
    assert result.cells_trimmed == 2


def test_missing_file_returns_error(tmp_csv):
    out = tmp_csv / "out.csv"
    result = trim_csv(str(tmp_csv / "nope.csv"), str(out), {"a": 5})
    assert result.errors
    assert "not found" in result.errors[0]


def test_unknown_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice"}], ["name"])
    result = trim_csv(str(src), str(out), {"ghost": 3})
    assert any("ghost" in e for e in result.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "hello"}], ["x"])
    result = trim_csv(str(src), str(out), {"x": 3})
    s = summary(result)
    assert "Cells trimmed" in s
    assert "Rows processed" in s
