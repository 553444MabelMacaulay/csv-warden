"""Tests for csv_warden/column_hasher.py"""
import csv
import hashlib
import pytest
from pathlib import Path
from csv_warden.column_hasher import hash_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path: Path, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def _read(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_hash_adds_suffix_column(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"name": "alice", "age": "30"}], ["name", "age"])
    r = hash_csv(str(src), str(out), columns=["name"])
    assert r.rows_processed == 1
    assert not r.errors
    rows = _read(out)
    assert "name_hashed" in rows[0]
    assert rows[0]["name"] == "alice"  # original preserved


def test_hash_replace_mode(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"email": "a@b.com"}], ["email"])
    r = hash_csv(str(src), str(out), columns=["email"], replace=True)
    rows = _read(out)
    expected = hashlib.sha256(b"a@b.com").hexdigest()
    assert rows[0]["email"] == expected
    assert "email_hashed" not in rows[0]


def test_hash_md5_algorithm(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"val": "hello"}], ["val"])
    r = hash_csv(str(src), str(out), columns=["val"], algorithm="md5")
    rows = _read(out)
    expected = hashlib.md5(b"hello").hexdigest()
    assert rows[0]["val_hashed"] == expected
    assert r.algorithm == "md5"


def test_missing_file_returns_error(tmp_csv):
    r = hash_csv("/no/such/file.csv", str(tmp_csv / "out.csv"), columns=["x"])
    assert r.errors
    assert "not found" in r.errors[0].lower()


def test_missing_column_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    r = hash_csv(str(src), str(out), columns=["z"])
    assert r.errors
    assert "z" in r.errors[0]


def test_unsupported_algorithm_returns_error(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"a": "1"}], ["a"])
    r = hash_csv(str(src), str(out), columns=["a"], algorithm="rot13")
    assert r.errors


def test_summary_output(tmp_csv):
    src = tmp_csv / "in.csv"
    out = tmp_csv / "out.csv"
    _write(src, [{"x": "v"}], ["x"])
    r = hash_csv(str(src), str(out), columns=["x"])
    s = summary(r)
    assert "sha256" in s
    assert "x" in s
    assert "1" in s
