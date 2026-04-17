import csv
import pytest
from pathlib import Path
from csv_warden.row_filter_expr import filter_by_expr, summary


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


def test_filter_numeric_gt(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}, {"name": "Carol", "age": "35"}])
    r = filter_by_expr(str(src), str(out), "age>29")
    rows = _read(out)
    assert r.output_rows == 2
    assert all(int(row["age"]) > 29 for row in rows)


def test_filter_string_eq(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    r = filter_by_expr(str(src), str(out), "name==Alice")
    rows = _read(out)
    assert r.output_rows == 1
    assert rows[0]["name"] == "Alice"


def test_filter_exclude_flag(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    r = filter_by_expr(str(src), str(out), "name==Alice", exclude=True)
    rows = _read(out)
    assert r.output_rows == 1
    assert rows[0]["name"] == "Bob"


def test_filter_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    r = filter_by_expr(str(tmp_csv / "nope.csv"), str(out), "age>10")
    assert r.errors
    assert "not found" in r.errors[0]


def test_filter_invalid_expr(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}])
    r = filter_by_expr(str(src), str(out), "bad_expression_no_op")
    assert r.skipped_rows == 1
    assert r.errors


def test_summary_string(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1"}, {"x": "2"}])
    r = filter_by_expr(str(src), str(out), "x==1")
    s = summary(r)
    assert "Input rows: 2" in s
    assert "Output rows: 1" in s
