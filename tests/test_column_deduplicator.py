import csv
import io
import pytest
from pathlib import Path
from csv_warden.column_deduplicator import dedupe_column, summary


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(rows, headers):
        p = tmp_path / "input.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_clears_consecutive_duplicates(tmp_csv, tmp_path):
    src = tmp_csv(
        [{"dept": "A", "name": "Alice"}, {"dept": "A", "name": "Bob"}, {"dept": "B", "name": "Carol"}],
        ["dept", "name"],
    )
    out = str(tmp_path / "out.csv")
    r = dedupe_column(src, out, column="dept")
    rows = _read(out)
    assert rows[0]["dept"] == "A"
    assert rows[1]["dept"] == ""
    assert rows[2]["dept"] == "B"
    assert r.cells_cleared == 1
    assert r.rows_processed == 3


def test_non_consecutive_duplicates_kept(tmp_csv, tmp_path):
    src = tmp_csv(
        [{"dept": "A"}, {"dept": "B"}, {"dept": "A"}],
        ["dept"],
    )
    out = str(tmp_path / "out.csv")
    r = dedupe_column(src, out, column="dept")
    rows = _read(out)
    assert rows[0]["dept"] == "A"
    assert rows[1]["dept"] == "B"
    assert rows[2]["dept"] == "A"
    assert r.cells_cleared == 0


def test_custom_fill_value(tmp_csv, tmp_path):
    src = tmp_csv([{"x": "1"}, {"x": "1"}], ["x"])
    out = str(tmp_path / "out.csv")
    dedupe_column(src, out, column="x", fill="N/A")
    rows = _read(out)
    assert rows[1]["x"] == "N/A"


def test_missing_column_returns_error(tmp_csv, tmp_path):
    src = tmp_csv([{"a": "1"}], ["a"])
    out = str(tmp_path / "out.csv")
    r = dedupe_column(src, out, column="z")
    assert r.errors
    assert "z" in r.errors[0]


def test_missing_file_returns_error(tmp_path):
    r = dedupe_column("no_such.csv", str(tmp_path / "out.csv"), column="x")
    assert r.errors


def test_summary_output(tmp_csv, tmp_path):
    src = tmp_csv([{"v": "a"}, {"v": "a"}], ["v"])
    out = str(tmp_path / "out.csv")
    r = dedupe_column(src, out, column="v")
    s = summary(r)
    assert "Cleared" in s
    assert "v" in s
