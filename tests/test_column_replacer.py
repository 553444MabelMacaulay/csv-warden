"""Tests for csv_warden.column_replacer."""
import csv
import pytest
from pathlib import Path
from csv_warden.column_replacer import replace_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows: list[list[str]]) -> Path:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_exact_replace(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["name", "city"], ["Alice", "New York"], ["Bob", "New York"], ["Carol", "Boston"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "city", "New York", "NYC")
    assert r.replacements_made == 2
    rows = _read(out)
    assert rows[0]["city"] == "NYC"
    assert rows[2]["city"] == "Boston"


def test_regex_replace(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["val"], ["foo123"], ["bar456"], ["baz"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "val", r"\d+", "NUM", use_regex=True)
    assert r.replacements_made == 2
    rows = _read(out)
    assert rows[0]["val"] == "fooNUM"
    assert rows[2]["val"] == "baz"


def test_ignore_case(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["name"], ["alice"], ["ALICE"], ["Bob"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "name", "alice", "X", ignore_case=True)
    assert r.replacements_made == 2


def test_column_not_found(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["a"], ["1"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "missing", "x", "y")
    assert r.errors
    assert "missing" in r.errors[0]


def test_file_not_found(tmp_csv):
    r = replace_csv("nonexistent.csv", str(tmp_csv / "out.csv"), "col", "a", "b")
    assert r.errors


def test_no_replacements(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["x"], ["hello"], ["world"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "x", "zzz", "YYY")
    assert r.replacements_made == 0


def test_summary_contains_key_info(tmp_csv):
    src = _write(tmp_csv / "in.csv", [["col"], ["abc"]])
    out = tmp_csv / "out.csv"
    r = replace_csv(str(src), str(out), "col", "abc", "xyz")
    s = summary(r)
    assert "col" in s
    assert "Replacements made" in s
