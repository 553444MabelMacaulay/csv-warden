import csv
import pytest
from pathlib import Path
from csv_warden.column_formatter import format_csv, summary, SUPPORTED_FORMATS


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_upper_format(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice", "city": "paris"}])
    result = format_csv(str(src), str(out), {"name": "upper"})
    assert not result.errors
    rows = _read(out)
    assert rows[0]["name"] == "ALICE"
    assert rows[0]["city"] == "paris"


def test_title_format(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice smith"}])
    result = format_csv(str(src), str(out), {"name": "title"})
    assert not result.errors
    assert _read(out)[0]["name"] == "Alice Smith"


def test_lower_format(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "HELLO"}])
    result = format_csv(str(src), str(out), {"name": "lower"})
    assert _read(out)[0]["name"] == "hello"


def test_strip_format(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "  bob  "}])
    result = format_csv(str(src), str(out), {"name": "strip"})
    assert _read(out)[0]["name"] == "bob"
    assert result.rows_affected == 1


def test_missing_file_returns_error(tmp_csv):
    result = format_csv("no_such.csv", str(tmp_csv / "out.csv"), {"name": "upper"})
    assert result.errors


def test_unsupported_format_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = format_csv(str(src), str(out), {"name": "reverse"})
    assert any("Unsupported" in e for e in result.errors)


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = format_csv(str(src), str(out), {"ghost": "upper"})
    assert any("ghost" in e for e in result.errors)


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = format_csv(str(src), str(out), {"name": "upper"})
    s = summary(result)
    assert "name" in s
    assert "Rows affected" in s
