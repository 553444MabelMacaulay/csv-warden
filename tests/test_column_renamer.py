import csv
import pytest
from pathlib import Path
from csv_warden.column_renamer import apply_prefix_suffix


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(rows):
        p = tmp_path / "input.csv"
        with open(p, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_add_prefix(tmp_csv, tmp_path):
    src = tmp_csv([{"name": "Alice", "age": "30"}])
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix(src, out, prefix="col_")
    assert result.success
    rows = _read(out)
    assert "col_name" in rows[0]
    assert "col_age" in rows[0]
    assert len(result.columns_renamed) == 2


def test_add_suffix(tmp_csv, tmp_path):
    src = tmp_csv([{"name": "Bob", "score": "99"}])
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix(src, out, suffix="_v2")
    assert result.success
    rows = _read(out)
    assert "name_v2" in rows[0]
    assert "score_v2" in rows[0]


def test_prefix_selected_columns_only(tmp_csv, tmp_path):
    src = tmp_csv([{"id": "1", "name": "Carol", "age": "25"}])
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix(src, out, prefix="raw_", columns=["name", "age"])
    assert result.success
    rows = _read(out)
    assert "id" in rows[0]
    assert "raw_name" in rows[0]
    assert "raw_age" in rows[0]
    assert len(result.columns_renamed) == 2


def test_missing_file_returns_error(tmp_path):
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix("nonexistent.csv", out, prefix="x_")
    assert not result.success
    assert "not found" in result.errors[0]


def test_no_prefix_or_suffix_returns_error(tmp_csv, tmp_path):
    src = tmp_csv([{"a": "1"}])
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix(src, out)
    assert not result.success


def test_summary_on_success(tmp_csv, tmp_path):
    src = tmp_csv([{"x": "1"}])
    out = str(tmp_path / "out.csv")
    result = apply_prefix_suffix(src, out, suffix="_end")
    assert "Renamed" in result.summary()


def test_data_values_preserved(tmp_csv, tmp_path):
    src = tmp_csv([{"city": "Paris", "pop": "2M"}])
    out = str(tmp_path / "out.csv")
    apply_prefix_suffix(src, out, prefix="d_")
    rows = _read(out)
    assert rows[0]["d_city"] == "Paris"
    assert rows[0]["d_pop"] == "2M"
