import csv
import io
import pytest
from pathlib import Path
from csv_warden.column_splitter import split_column, summary


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(rows, headers):
        p = tmp_path / "input.csv"
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
        return str(p)
    return _write


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_split_basic(tmp_csv, tmp_path):
    src = tmp_csv([{"name": "John Doe", "age": "30"}], ["name", "age"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "name", " ")
    assert not result.errors
    rows = _read(out)
    assert rows[0]["name_0"] == "John"
    assert rows[0]["name_1"] == "Doe"
    assert rows[0]["age"] == "30"


def test_split_custom_column_names(tmp_csv, tmp_path):
    src = tmp_csv([{"full": "a-b-c"}], ["full"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "full", "-", new_columns=["x", "y", "z"])
    assert not result.errors
    rows = _read(out)
    assert rows[0]["x"] == "a"
    assert rows[0]["y"] == "b"
    assert rows[0]["z"] == "c"


def test_split_drop_original(tmp_csv, tmp_path):
    src = tmp_csv([{"email": "user@example.com"}], ["email"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "email", "@", drop_original=True)
    assert not result.errors
    rows = _read(out)
    assert "email" not in rows[0]
    assert rows[0]["email_0"] == "user"


def test_split_missing_column(tmp_csv, tmp_path):
    src = tmp_csv([{"a": "1"}], ["a"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "b", ",")
    assert any("not found" in e for e in result.errors)


def test_split_missing_file(tmp_path):
    out = str(tmp_path / "out.csv")
    result = split_column("nonexistent.csv", out, "col", ",")
    assert any("not found" in e for e in result.errors)


def test_split_uneven_parts(tmp_csv, tmp_path):
    src = tmp_csv([{"v": "a,b,c"}, {"v": "x,y"}], ["v"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "v", ",")
    assert not result.errors
    rows = _read(out)
    assert rows[1]["v_2"] == ""


def test_summary_output(tmp_csv, tmp_path):
    src = tmp_csv([{"col": "a|b"}], ["col"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "col", "|")
    s = summary(result)
    assert "col" in s
    assert "|" in s


def test_split_no_separator_match(tmp_csv, tmp_path):
    """When the delimiter is not found in a value, the whole value goes into column_0."""
    src = tmp_csv([{"tag": "python"}], ["tag"])
    out = str(tmp_path / "out.csv")
    result = split_column(src, out, "tag", ",")
    assert not result.errors
    rows = _read(out)
    assert rows[0]["tag_0"] == "python"
