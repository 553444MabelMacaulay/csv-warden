import csv
import pytest
from pathlib import Path
from csv_warden.column_normalizer import normalize_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_snake_case_normalize(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "Hello World", "age": "25"}, {"name": "Foo-Bar", "age": "30"}])
    result = normalize_csv(str(src), str(out), columns=["name"], mode="snake_case")
    assert result.rows_processed == 2
    rows = _read(out)
    assert rows[0]["name"] == "hello_world"
    assert rows[1]["name"] == "foo_bar"
    assert rows[0]["age"] == "25"


def test_upper_normalize(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"city": "london"}, {"city": "paris"}])
    result = normalize_csv(str(src), str(out), columns=["city"], mode="upper")
    rows = _read(out)
    assert rows[0]["city"] == "LONDON"
    assert rows[1]["city"] == "PARIS"


def test_lower_normalize(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"city": "LONDON"}, {"city": "PARIS"}])
    result = normalize_csv(str(src), str(out), columns=["city"], mode="lower")
    rows = _read(out)
    assert rows[0]["city"] == "london"


def test_title_case_normalize(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "john doe"}])
    result = normalize_csv(str(src), str(out), columns=["name"], mode="title_case")
    rows = _read(out)
    assert rows[0]["name"] == "John Doe"


def test_missing_file(tmp_csv):
    result = normalize_csv(str(tmp_csv / "no.csv"), str(tmp_csv / "out.csv"), ["col"])
    assert result.errors
    assert "not found" in result.errors[0]


def test_missing_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = normalize_csv(str(src), str(out), columns=["nonexistent"])
    assert result.errors
    assert "nonexistent" in result.errors[0]


def test_unsupported_mode(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = normalize_csv(str(src), str(out), columns=["name"], mode="camel")
    assert result.errors
    assert "Unsupported mode" in result.errors[0]


def test_summary_ok(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice"}])
    result = normalize_csv(str(src), str(out), columns=["name"], mode="upper")
    s = summary(result)
    assert "OK" in s
    assert "name" in s
