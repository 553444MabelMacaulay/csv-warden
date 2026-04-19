import csv
import pytest
from pathlib import Path
from csv_warden.column_outlier import detect_outliers, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_zscore_flags_outlier(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [1, 2, 2, 2, 2, 2, 2, 100]]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="val", method="zscore", threshold=2.0)
    assert r.rows_flagged >= 1
    data = _read(out)
    flagged = [row for row in data if row["_outlier"] == "1"]
    assert any(row["val"] == "100" for row in flagged)


def test_iqr_flags_outlier(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [10, 11, 10, 12, 10, 11, 200]]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="val", method="iqr", threshold=1.5)
    assert r.rows_flagged >= 1


def test_no_outliers_all_flagged_zero(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [5, 5, 5, 5, 5]]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="val", method="zscore")
    assert r.rows_flagged == 0
    data = _read(out)
    assert all(row["_outlier"] == "0" for row in data)


def test_missing_file_returns_error(tmp_csv):
    out = tmp_csv / "out.csv"
    r = detect_outliers(str(tmp_csv / "nope.csv"), str(out), column="val")
    assert r.errors
    assert "not found" in r.errors[0].lower()


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"x": "1"}, {"x": "2"}]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="missing")
    assert r.errors


def test_unknown_method_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [1, 2, 3]]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="val", method="bogus")
    assert r.errors


def test_custom_flag_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [1, 1, 1, 999]]
    _write(src, rows)
    detect_outliers(str(src), str(out), column="val", flag_column="is_outlier")
    data = _read(out)
    assert "is_outlier" in data[0]


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    rows = [{"val": str(v)} for v in [1, 2, 3, 100]]
    _write(src, rows)
    r = detect_outliers(str(src), str(out), column="val")
    s = summary(r)
    assert "Flagged" in s
    assert "zscore" in s
