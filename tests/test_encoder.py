"""Tests for csv_warden.encoder."""
import csv
from pathlib import Path

import pytest

from csv_warden.encoder import encode_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, encoding="utf-8"):
    with path.open("w", encoding=encoding, newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path, encoding="utf-8"):
    with path.open(encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh))


def test_encode_utf8_to_latin1(tmp_csv):
    src = tmp_csv / "src.csv"
    dst = tmp_csv / "dst.csv"
    _write(src, [{"name": "Alice", "city": "Paris"}, {"name": "Bob", "city": "Lyon"}])
    result = encode_csv(str(src), str(dst), source_encoding="utf-8", target_encoding="latin-1")
    assert result.success
    assert result.rows_written == 2
    rows = _read(dst, encoding="latin-1")
    assert rows[0]["name"] == "Alice"


def test_encode_same_encoding(tmp_csv):
    src = tmp_csv / "src.csv"
    dst = tmp_csv / "dst.csv"
    _write(src, [{"a": "1"}, {"a": "2"}])
    result = encode_csv(str(src), str(dst))
    assert result.success
    assert result.rows_written == 2


def test_missing_file(tmp_csv):
    result = encode_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"))
    assert not result.success
    assert any("not found" in e for e in result.errors)


def test_invalid_target_encoding(tmp_csv):
    src = tmp_csv / "src.csv"
    dst = tmp_csv / "dst.csv"
    _write(src, [{"x": "hello"}])
    result = encode_csv(str(src), str(dst), target_encoding="not-a-real-encoding-xyz")
    assert not result.success
    assert result.errors


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "src.csv"
    dst = tmp_csv / "dst.csv"
    _write(src, [{"col": "val"}])
    result = encode_csv(str(src), str(dst), source_encoding="utf-8", target_encoding="utf-8")
    s = summary(result)
    assert "utf-8" in s
    assert "Rows written" in s
    assert "OK" in s
