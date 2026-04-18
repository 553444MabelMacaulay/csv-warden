import csv
import pytest
from pathlib import Path
from csv_warden.column_counter import count_csv


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(rows, filename="test.csv"):
        p = tmp_path / filename
        with open(p, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_basic_count(tmp_csv, tmp_path):
    src = tmp_csv([
        {"dept": "eng", "name": "Alice"},
        {"dept": "eng", "name": "Bob"},
        {"dept": "hr", "name": "Carol"},
    ])
    out = str(tmp_path / "out.csv")
    result = count_csv(src, "dept", out)
    assert result.success()
    assert result.rows_in == 3
    assert result.rows_out == 2
    rows = _read(out)
    counts = {r["dept"]: int(r["count"]) for r in rows}
    assert counts["eng"] == 2
    assert counts["hr"] == 1


def test_missing_file(tmp_path):
    result = count_csv("nonexistent.csv", "dept", str(tmp_path / "out.csv"))
    assert not result.success()
    assert any("not found" in e for e in result.errors)


def test_missing_group_column(tmp_csv, tmp_path):
    src = tmp_csv([{"a": "1", "b": "2"}])
    out = str(tmp_path / "out.csv")
    result = count_csv(src, "dept", out)
    assert not result.success()
    assert any("dept" in e for e in result.errors)


def test_count_column_skips_empty(tmp_csv, tmp_path):
    src = tmp_csv([
        {"dept": "eng", "score": "10"},
        {"dept": "eng", "score": ""},
        {"dept": "hr", "score": "5"},
    ])
    out = str(tmp_path / "out.csv")
    result = count_csv(src, "dept", out, count_column="score")
    assert result.success()
    rows = _read(out)
    counts = {r["dept"]: int(r["count"]) for r in rows}
    assert counts["eng"] == 1
    assert counts["hr"] == 1


def test_custom_result_header(tmp_csv, tmp_path):
    src = tmp_csv([{"cat": "a"}, {"cat": "a"}, {"cat": "b"}])
    out = str(tmp_path / "out.csv")
    result = count_csv(src, "cat", out, result_header="total")
    assert result.success()
    rows = _read(out)
    assert "total" in rows[0]


def test_summary_contains_key_info(tmp_csv, tmp_path):
    src = tmp_csv([{"dept": "eng", "name": "Alice"}])
    out = str(tmp_path / "out.csv")
    result = count_csv(src, "dept", out)
    s = result.summary()
    assert "dept" in s
    assert "Rows in" in s
    assert "Groups out" in s
