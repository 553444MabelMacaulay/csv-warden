"""Tests for csv_warden.splitter."""

import csv
import os
import pytest

from csv_warden.splitter import split_csv, summary


@pytest.fixture()
def tmp_csv(tmp_path):
    return tmp_path


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


DATA = [
    {"region": "north", "value": "10"},
    {"region": "south", "value": "20"},
    {"region": "north", "value": "30"},
    {"region": "east", "value": "40"},
]


def test_split_by_column(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out"
    _write(src, DATA)
    result = split_csv(str(src), str(out), column="region")
    assert result.errors == []
    assert result.chunks == 3
    assert result.rows_written == 4
    assert os.path.exists(out / "north.csv")
    assert len(_read(out / "north.csv")) == 2


def test_split_by_chunk_size(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "chunks"
    _write(src, DATA)
    result = split_csv(str(src), str(out), chunk_size=2)
    assert result.errors == []
    assert result.chunks == 2
    assert result.rows_written == 4
    assert len(_read(out / "chunk_0001.csv")) == 2
    assert len(_read(out / "chunk_0002.csv")) == 2


def test_split_missing_file(tmp_csv):
    result = split_csv(str(tmp_csv / "nope.csv"), str(tmp_csv / "out"), column="x")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_split_missing_column(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, DATA)
    result = split_csv(str(src), str(tmp_csv / "out"), column="nonexistent")
    assert result.errors
    assert "not found" in result.errors[0].lower()


def test_split_no_mode_raises_error(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, DATA)
    result = split_csv(str(src), str(tmp_csv / "out"))
    assert result.errors


def test_split_both_modes_raises_error(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, DATA)
    result = split_csv(str(src), str(tmp_csv / "out"), column="region", chunk_size=2)
    assert result.errors


def test_invalid_chunk_size(tmp_csv):
    src = tmp_csv / "data.csv"
    _write(src, DATA)
    result = split_csv(str(src), str(tmp_csv / "out"), chunk_size=0)
    assert result.errors


def test_summary_contains_chunks(tmp_csv):
    src = tmp_csv / "data.csv"
    out = tmp_csv / "out"
    _write(src, DATA)
    result = split_csv(str(src), str(out), chunk_size=3)
    text = summary(result)
    assert "Chunks" in text
    assert "chunk_0001.csv" in text
