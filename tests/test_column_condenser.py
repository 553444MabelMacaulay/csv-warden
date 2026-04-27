"""Tests for csv_warden.column_condenser."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_condenser import condense_csv, summary


@pytest.fixture()
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


def test_basic_condense(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"first": "Alice", "last": "Smith"}, {"first": "Bob", "last": "Jones"}])
    result = condense_csv(str(src), str(out), "{first} {last}", "full_name")
    assert result.rows_processed == 2
    assert result.rows_failed == 0
    rows = _read(out)
    assert rows[0]["full_name"] == "Alice Smith"
    assert rows[1]["full_name"] == "Bob Jones"


def test_original_columns_preserved(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    condense_csv(str(src), str(out), "{a}-{b}", "combo")
    rows = _read(out)
    assert "a" in rows[0]
    assert "b" in rows[0]
    assert "combo" in rows[0]


def test_drop_sources(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "hello", "y": "world", "z": "!"}])
    condense_csv(str(src), str(out), "{x} {y}", "msg", drop_sources=True)
    rows = _read(out)
    assert "x" not in rows[0]
    assert "y" not in rows[0]
    assert "z" in rows[0]
    assert rows[0]["msg"] == "hello world"


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = condense_csv(str(tmp_csv / "nope.csv"), str(out), "{a}", "col")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_missing_placeholder_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = condense_csv(str(src), str(out), "{a} {b}", "combo")
    assert result.errors
    assert "b" in result.errors[0]


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"col": "val"}])
    result = condense_csv(str(src), str(out), "{col}", "new")
    s = summary(result)
    assert "new" in s
    assert "Rows processed" in s


def test_static_text_in_template(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"code": "42"}])
    condense_csv(str(src), str(out), "ID:{code}", "label")
    rows = _read(out)
    assert rows[0]["label"] == "ID:42"
