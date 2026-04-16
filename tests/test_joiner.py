import pytest
from pathlib import Path
import csv
from csv_warden.joiner import join_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(name, rows):
        p = tmp_path / name
        with open(p, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return p
    return _write


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_inner_join(tmp_csv, tmp_path):
    left = tmp_csv("left.csv", [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}, {"id": "3", "name": "Carol"}])
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}, {"id": "2", "score": "85"}])
    out = tmp_path / "out.csv"
    r = join_csv(left, right, "id", out, join_type="inner")
    assert r.output_rows == 2
    assert not r.errors
    rows = _read(out)
    assert rows[0]["name"] == "Alice"
    assert rows[0]["score"] == "90"


def test_left_join(tmp_csv, tmp_path):
    left = tmp_csv("left.csv", [{"id": "1", "name": "Alice"}, {"id": "3", "name": "Carol"}])
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}])
    out = tmp_path / "out.csv"
    r = join_csv(left, right, "id", out, join_type="left")
    assert r.output_rows == 2
    rows = _read(out)
    carol = next(row for row in rows if row["name"] == "Carol")
    assert carol["score"] == ""


def test_right_join(tmp_csv, tmp_path):
    left = tmp_csv("left.csv", [{"id": "1", "name": "Alice"}])
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}, {"id": "2", "score": "75"}])
    out = tmp_path / "out.csv"
    r = join_csv(left, right, "id", out, join_type="right")
    assert r.output_rows == 2


def test_missing_left_file(tmp_csv, tmp_path):
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}])
    out = tmp_path / "out.csv"
    r = join_csv(tmp_path / "nope.csv", right, "id", out)
    assert r.errors


def test_missing_key(tmp_csv, tmp_path):
    left = tmp_csv("left.csv", [{"id": "1", "name": "Alice"}])
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}])
    out = tmp_path / "out.csv"
    r = join_csv(left, right, "bad_key", out)
    assert r.errors


def test_summary_contains_join_type(tmp_csv, tmp_path):
    left = tmp_csv("left.csv", [{"id": "1", "name": "Alice"}])
    right = tmp_csv("right.csv", [{"id": "1", "score": "90"}])
    out = tmp_path / "out.csv"
    r = join_csv(left, right, "id", out, join_type="left")
    s = summary(r)
    assert "left" in s
    assert "Output rows" in s
