"""Tests for csv_warden.column_truncator."""
import csv
import io
import pytest
from pathlib import Path

from csv_warden.column_truncator import truncate_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[list[str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_missing_file(tmp_csv):
    result = truncate_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out.csv"), "name", 5)
    assert result.errors
    assert "not found" in result.errors[0]


def test_column_not_found(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["a", "b"], ["hello", "world"]])
    result = truncate_csv(str(src), str(tmp_csv / "out.csv"), "missing", 3)
    assert result.errors
    assert "not found" in result.errors[0]


def test_truncates_long_values(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["name"], ["Alexander"], ["Bo"], ["Christopher"]])
    out = tmp_csv / "out.csv"
    result = truncate_csv(str(src), str(out), "name", 5)
    assert result.rows_total == 3
    assert result.rows_truncated == 2
    rows = _read(out)
    assert rows[0]["name"] == "Alexa"
    assert rows[1]["name"] == "Bo"
    assert rows[2]["name"] == "Chris"


def test_suffix_appended(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["text"], ["Hello World"]])
    out = tmp_csv / "out.csv"
    result = truncate_csv(str(src), str(out), "text", 5, suffix="...")
    rows = _read(out)
    assert rows[0]["text"] == "Hello..."
    assert result.rows_truncated == 1


def test_no_truncation_when_within_limit(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["word"], ["hi"], ["ok"]])
    out = tmp_csv / "out.csv"
    result = truncate_csv(str(src), str(out), "word", 10)
    assert result.rows_truncated == 0
    rows = _read(out)
    assert rows[0]["word"] == "hi"


def test_max_length_zero(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["val"], ["abc"]])
    out = tmp_csv / "out.csv"
    result = truncate_csv(str(src), str(out), "val", 0)
    rows = _read(out)
    assert rows[0]["val"] == ""
    assert result.rows_truncated == 1


def test_negative_max_length_error(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["val"], ["abc"]])
    result = truncate_csv(str(src), str(tmp_csv / "out.csv"), "val", -1)
    assert result.errors
    assert "max_length" in result.errors[0]


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "in.csv"
    _write(src, [["name"], ["Alexander"]])
    out = tmp_csv / "out.csv"
    result = truncate_csv(str(src), str(out), "name", 4)
    s = summary(result)
    assert "name" in s
    assert "4" in s
    assert "Truncated" in s
