import csv
import subprocess
import sys
import pytest
from pathlib import Path


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dept", "name"])
        w.writerow(["Eng", "Alice"])
        w.writerow(["Eng", "Bob"])
        w.writerow(["HR", "Carol"])
    return str(p)


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden.cli"] + args,
        capture_output=True, text=True
    )


def test_dedupe_col_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    r = _run(["dedupe-col", simple_csv, "--column", "dept", "--output", out])
    assert r.returncode == 0


def test_dedupe_col_clears_repeat(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    _run(["dedupe-col", simple_csv, "--column", "dept", "--output", out])
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["dept"] == "Eng"
    assert rows[1]["dept"] == ""
    assert rows[2]["dept"] == "HR"


def test_dedupe_col_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    r = _run(["dedupe-col", "ghost.csv", "--column", "dept", "--output", out])
    assert r.returncode == 1


def test_dedupe_col_bad_column_exits_one(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    r = _run(["dedupe-col", simple_csv, "--column", "zzz", "--output", out])
    assert r.returncode == 1


def test_dedupe_col_summary_in_output(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    r = _run(["dedupe-col", simple_csv, "--column", "dept", "--output", out])
    assert "Cleared" in r.stdout or "dept" in r.stdout
