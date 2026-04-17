import csv
import pytest
from pathlib import Path
from csv_warden.column_mapper import map_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if not rows:
        return
    fn = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_map_replaces_values(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"status": "0"}, {"status": "1"}, {"status": "0"}])
    r = map_csv(str(src), str(out), "status", {"0": "inactive", "1": "active"})
    assert r.mapped == 3
    assert r.unmapped == 0
    rows = _read(out)
    assert rows[0]["status"] == "inactive"
    assert rows[1]["status"] == "active"


def test_unmapped_kept_when_no_default(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "a"}, {"x": "b"}])
    r = map_csv(str(src), str(out), "x", {"a": "A"})
    assert r.mapped == 1
    assert r.unmapped == 1
    rows = _read(out)
    assert rows[1]["x"] == "b"  # unchanged


def test_unmapped_replaced_with_default(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "a"}, {"x": "z"}])
    r = map_csv(str(src), str(out), "x", {"a": "A"}, default="unknown")
    rows = _read(out)
    assert rows[1]["x"] == "unknown"
    assert r.unmapped == 1


def test_missing_file_returns_error(tmp_csv):
    out = tmp_csv / "out.csv"
    r = map_csv(str(tmp_csv / "nope.csv"), str(out), "col", {})
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}])
    r = map_csv(str(src), str(out), "z", {"1": "one"})
    assert any("not found" in e for e in r.errors)


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"v": "yes"}, {"v": "no"}])
    r = map_csv(str(src), str(out), "v", {"yes": "Y", "no": "N"})
    s = summary(r)
    assert "Mapped" in s
    assert "v" in s
