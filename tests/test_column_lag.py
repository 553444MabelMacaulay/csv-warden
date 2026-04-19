import csv
import io
import pytest
from pathlib import Path
from csv_warden.column_lag import lag_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_lag_adds_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": str(i)} for i in range(5)])
    r = lag_csv(str(src), str(out), column="val", n=1)
    assert r.rows_written == 5
    rows = _read(out)
    assert "val_lag1" in rows[0]
    assert rows[0]["val_lag1"] == ""
    assert rows[1]["val_lag1"] == "0"
    assert rows[4]["val_lag1"] == "3"


def test_lag_n2(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": str(i)} for i in range(5)])
    lag_csv(str(src), str(out), column="x", n=2)
    rows = _read(out)
    assert rows[0]["x_lag2"] == ""
    assert rows[1]["x_lag2"] == ""
    assert rows[2]["x_lag2"] == "0"


def test_lead_negative_n(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": str(i)} for i in range(4)])
    lag_csv(str(src), str(out), column="x", n=-1)
    rows = _read(out)
    assert rows[0]["x_lag-1"] == "1"
    assert rows[3]["x_lag-1"] == ""


def test_custom_new_column_name(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": str(i)} for i in range(3)])
    lag_csv(str(src), str(out), column="v", n=1, new_column="prev_v")
    rows = _read(out)
    assert "prev_v" in rows[0]


def test_fill_value(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": str(i)} for i in range(3)])
    lag_csv(str(src), str(out), column="v", n=1, fill_value="NA")
    rows = _read(out)
    assert rows[0]["v_lag1"] == "NA"


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    r = lag_csv(str(tmp_csv / "nope.csv"), str(out), column="v")
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = lag_csv(str(src), str(out), column="z")
    assert any("not found" in e for e in r.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": str(i)} for i in range(3)])
    r = lag_csv(str(src), str(out), column="v", n=1)
    s = summary(r)
    assert "v" in s
    assert "1" in s
