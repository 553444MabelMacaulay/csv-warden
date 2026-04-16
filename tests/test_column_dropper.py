import csv
import pytest
from pathlib import Path
from csv_warden.column_dropper import drop_columns, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows and fieldnames is None:
        raise ValueError("provide fieldnames for empty csv")
    fn = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_drop_single_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2", "c": "3"}, {"a": "4", "b": "5", "c": "6"}])
    result = drop_columns(str(src), str(out), ["b"])
    assert result.columns_dropped == ["b"]
    assert result.columns_not_found == []
    assert result.rows_written == 2
    rows = _read(out)
    assert all("b" not in r for r in rows)
    assert all("a" in r and "c" in r for r in rows)


def test_drop_multiple_columns(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1", "y": "2", "z": "3"}])
    result = drop_columns(str(src), str(out), ["x", "z"])
    assert set(result.columns_dropped) == {"x", "z"}
    rows = _read(out)
    assert rows[0].keys() == {"y"}


def test_column_not_found(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = drop_columns(str(src), str(out), ["missing"])
    assert "missing" in result.columns_not_found
    assert result.columns_dropped == []
    rows = _read(out)
    assert len(rows) == 1


def test_missing_input_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = drop_columns(str(tmp_csv / "nope.csv"), str(out), ["a"])
    assert result.errors
    assert not out.exists()


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1", "b": "2"}])
    result = drop_columns(str(src), str(out), ["a"])
    s = summary(result)
    assert "Columns dropped" in s
    assert "a" in s


def test_rows_written_count(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    data = [{"col1": str(i), "col2": str(i * 2)} for i in range(10)]
    _write(src, data)
    result = drop_columns(str(src), str(out), ["col2"])
    assert result.rows_written == 10
