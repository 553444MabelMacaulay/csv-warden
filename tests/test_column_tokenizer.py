"""Tests for csv_warden.column_tokenizer."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_tokenizer import tokenize_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[dict], fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_basic_tokenize(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"text": "hello world hello"}])
    r = tokenize_csv(str(src), str(out), column="text")
    assert r.rows_processed == 1
    assert r.rows_failed == 0
    rows = _read(out)
    assert rows[0]["token_count"] == "3"
    assert rows[0]["unique_token_count"] == "2"


def test_empty_text_gives_zero(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"text": ""}])
    r = tokenize_csv(str(src), str(out), column="text")
    rows = _read(out)
    assert rows[0]["token_count"] == "0"
    assert rows[0]["unique_token_count"] == "0"


def test_custom_output_column_names(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"body": "foo bar baz"}])
    tokenize_csv(str(src), str(out), column="body", count_col="cnt", unique_col="ucnt")
    rows = _read(out)
    assert "cnt" in rows[0]
    assert "ucnt" in rows[0]


def test_missing_file_returns_error(tmp_csv):
    out = tmp_csv / "out.csv"
    r = tokenize_csv(str(tmp_csv / "nope.csv"), str(out), column="text")
    assert r.errors
    assert "not found" in r.errors[0]


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"other": "data"}])
    r = tokenize_csv(str(src), str(out), column="text")
    assert r.errors
    assert "not found" in r.errors[0]


def test_multiple_rows(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"text": "a b c"}, {"text": "x x x x"}, {"text": "one"}])
    r = tokenize_csv(str(src), str(out), column="text")
    assert r.rows_processed == 3
    rows = _read(out)
    assert rows[1]["token_count"] == "4"
    assert rows[1]["unique_token_count"] == "1"


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"text": "hello"}])
    r = tokenize_csv(str(src), str(out), column="text")
    s = summary(r)
    assert "text" in s
    assert "Processed" in s
