import csv
import pytest
from pathlib import Path
from csv_warden.pivotter import pivot_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(name, rows):
        p = tmp_path / name
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_basic_pivot(tmp_csv, tmp_path):
    src = tmp_csv("in.csv", [
        {"name": "Alice", "subject": "math", "score": "90"},
        {"name": "Alice", "subject": "english", "score": "85"},
        {"name": "Bob",   "subject": "math", "score": "70"},
        {"name": "Bob",   "subject": "english", "score": "80"},
    ])
    out = str(tmp_path / "out.csv")
    r = pivot_csv(src, out, "name", "subject", "score")
    assert r.rows_read == 4
    assert r.rows_written == 2
    assert not r.errors
    rows = _read(out)
    assert set(rows[0].keys()) == {"name", "math", "english"}
    alice = next(row for row in rows if row["name"] == "Alice")
    assert alice["math"] == "90"
    assert alice["english"] == "85"


def test_pivot_sum_aggfunc(tmp_csv, tmp_path):
    src = tmp_csv("in.csv", [
        {"region": "north", "product": "A", "sales": "10"},
        {"region": "north", "product": "A", "sales": "20"},
        {"region": "south", "product": "A", "sales": "5"},
    ])
    out = str(tmp_path / "out.csv")
    r = pivot_csv(src, out, "region", "product", "sales", aggfunc="sum")
    assert not r.errors
    rows = _read(out)
    north = next(row for row in rows if row["region"] == "north")
    assert north["A"] == "30.0"


def test_pivot_count_aggfunc(tmp_csv, tmp_path):
    src = tmp_csv("in.csv", [
        {"dept": "eng", "level": "senior", "emp": "Alice"},
        {"dept": "eng", "level": "senior", "emp": "Bob"},
        {"dept": "eng", "level": "junior", "emp": "Carol"},
    ])
    out = str(tmp_path / "out.csv")
    r = pivot_csv(src, out, "dept", "level", "emp", aggfunc="count")
    assert not r.errors
    rows = _read(out)
    assert rows[0]["senior"] == "2"
    assert rows[0]["junior"] == "1"


def test_missing_file(tmp_path):
    r = pivot_csv("no_such.csv", str(tmp_path / "out.csv"), "a", "b", "c")
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column(tmp_csv, tmp_path):
    src = tmp_csv("in.csv", [{"x": "1", "y": "2"}])
    out = str(tmp_path / "out.csv")
    r = pivot_csv(src, out, "x", "missing_col", "y")
    assert any("missing_col" in e for e in r.errors)


def test_summary_contains_key_info(tmp_csv, tmp_path):
    src = tmp_csv("in.csv", [
        {"a": "1", "b": "x", "c": "v"},
    ])
    out = str(tmp_path / "out.csv")
    r = pivot_csv(src, out, "a", "b", "c")
    s = summary(r)
    assert "Rows read" in s
    assert "Rows written" in s
