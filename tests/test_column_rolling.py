import csv
import pytest
from pathlib import Path
from csv_warden.column_rolling import rolling_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_rolling_mean(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": str(v)} for v in [1, 2, 3, 4, 5]])
    r = rolling_csv(str(src), str(out), "val", window=3, func="mean")
    rows = _read(out)
    assert r.rows_processed == 5
    assert float(rows[2]["val_rolling_mean"]) == pytest.approx(2.0)
    assert float(rows[4]["val_rolling_mean"]) == pytest.approx(4.0)


def test_rolling_sum(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": str(v)} for v in [1, 2, 3]])
    r = rolling_csv(str(src), str(out), "val", window=2, func="sum")
    rows = _read(out)
    assert float(rows[1]["val_rolling_sum"]) == pytest.approx(3.0)
    assert float(rows[2]["val_rolling_sum"]) == pytest.approx(5.0)


def test_rolling_min_max(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": str(v)} for v in [5, 1, 3, 2, 4]])
    r = rolling_csv(str(src), str(out), "val", window=3, func="min")
    rows = _read(out)
    assert float(rows[4]["val_rolling_min"]) == pytest.approx(2.0)


def test_custom_new_column_name(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "1"}, {"x": "2"}])
    rolling_csv(str(src), str(out), "x", window=2, func="mean", new_column="x_avg")
    rows = _read(out)
    assert "x_avg" in rows[0]


def test_missing_file(tmp_csv):
    r = rolling_csv(str(tmp_csv / "no.csv"), str(tmp_csv / "out.csv"), "val", 3)
    assert r.errors
    assert "not found" in r.errors[0]


def test_column_not_found(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = rolling_csv(str(src), str(out), "missing", 2)
    assert r.errors


def test_unsupported_func(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "1"}])
    r = rolling_csv(str(src), str(out), "v", 2, func="median")
    assert r.errors


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": str(i)} for i in range(4)])
    r = rolling_csv(str(src), str(out), "v", 2)
    s = summary(r)
    assert "Window" in s
    assert "mean" in s
