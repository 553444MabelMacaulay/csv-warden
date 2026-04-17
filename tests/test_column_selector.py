import csv
import pytest
from pathlib import Path
from csv_warden.column_selector import select_columns


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows and fieldnames is None:
        path.write_text("")
        return
    fn = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_select_single_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}])
    result = select_columns(str(src), str(out), ["name"])
    assert result.success()
    rows = _read(out)
    assert all("name" in r and "age" not in r for r in rows)
    assert result.rows_written == 2


def test_select_multiple_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2", "c": "3"}])
    result = select_columns(str(src), str(out), ["a", "c"])
    assert result.success()
    rows = _read(out)
    assert list(rows[0].keys()) == ["a", "c"]


def test_missing_columns_reported(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1", "y": "2"}])
    result = select_columns(str(src), str(out), ["x", "z"])
    assert result.success()
    assert "z" in result.missing_columns
    assert "x" in result.selected_columns


def test_all_columns_missing_fails(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    result = select_columns(str(src), str(out), ["x", "y"])
    assert not result.success()
    assert "None of the specified columns" in result.error


def test_file_not_found(tmp_csv):
    result = select_columns(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), ["a"])
    assert not result.success()
    assert "not found" in result.error


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"col1": "v", "col2": "w"}])
    result = select_columns(str(src), str(out), ["col1"])
    s = result.summary()
    assert "col1" in s
    assert "Rows" in s
