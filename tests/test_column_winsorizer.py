"""Tests for csv_warden.column_winsorizer."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_winsorizer import winsorize_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames: list[str]):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_missing_file(tmp_csv):
    result = winsorize_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), ["val"])
    assert result.errors
    assert "not found" in result.errors[0]


def test_column_not_found(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [{"a": "1"}], ["a"])
    result = winsorize_csv(str(src), str(tmp_csv / "out.csv"), ["missing"])
    assert any("missing" in e for e in result.errors)


def test_caps_high_values(tmp_csv):
    src = tmp_csv / "in.csv"
    rows = [{"val": str(i)} for i in range(1, 21)]  # 1..20
    _write(src, rows, ["val"])
    out = tmp_csv / "out.csv"
    result = winsorize_csv(str(src), str(out), ["val"], lower_pct=5, upper_pct=90)
    assert result.rows_affected > 0
    data = _read(out)
    values = [float(r["val"]) for r in data]
    assert max(values) <= 19.0  # 90th pct of 1..20


def test_caps_low_values(tmp_csv):
    src = tmp_csv / "in.csv"
    rows = [{"val": str(i)} for i in range(1, 21)]
    _write(src, rows, ["val"])
    out = tmp_csv / "out.csv"
    winsorize_csv(str(src), str(out), ["val"], lower_pct=10, upper_pct=100)
    data = _read(out)
    values = [float(r["val"]) for r in data]
    assert min(values) >= 2.9


def test_no_change_within_bounds(tmp_csv):
    src = tmp_csv / "in.csv"
    rows = [{"val": "5"}, {"val": "5"}, {"val": "5"}]
    _write(src, rows, ["val"])
    out = tmp_csv / "out.csv"
    result = winsorize_csv(str(src), str(out), ["val"], lower_pct=5, upper_pct=95)
    assert result.rows_affected == 0


def test_non_numeric_skipped(tmp_csv):
    src = tmp_csv / "in.csv"
    rows = [{"val": "abc"}, {"val": "def"}]
    _write(src, rows, ["val"])
    out = tmp_csv / "out.csv"
    result = winsorize_csv(str(src), str(out), ["val"])
    assert any("No numeric" in e for e in result.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    rows = [{"val": str(i)} for i in range(1, 11)]
    _write(src, rows, ["val"])
    out = tmp_csv / "out.csv"
    result = winsorize_csv(str(src), str(out), ["val"])
    s = summary(result)
    assert "val" in s
    assert "Rows affected" in s
