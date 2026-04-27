"""CLI integration tests for the shift-col sub-command."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("value,label\n10,a\n20,b\n30,c\n", encoding="utf-8")
    return p


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden"] + args,
        capture_output=True,
        text=True,
    )


def test_shift_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["shift-col", str(simple_csv), str(out), "--column", "value", "--offset", "5"])
    assert r.returncode == 0


def test_shift_col_output_offset_applied(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["shift-col", str(simple_csv), str(out), "--column", "value", "--offset", "5"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[0]["value"] == "15"
    assert rows[1]["value"] == "25"
    assert rows[2]["value"] == "35"


def test_shift_col_scale_applied(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["shift-col", str(simple_csv), str(out), "--column", "value", "--scale", "2"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[0]["value"] == "20"
    assert rows[2]["value"] == "60"


def test_shift_col_suffix_creates_new_column(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "shift-col", str(simple_csv), str(out),
        "--column", "value", "--offset", "1", "--suffix", "_new",
    ])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert "value" in rows[0]
    assert "value_new" in rows[0]
    assert rows[0]["value"] == "10"
    assert rows[0]["value_new"] == "11"


def test_shift_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["shift-col", "/no/such/file.csv", str(out), "--column", "value"])
    assert r.returncode == 1


def test_shift_col_summary_in_stdout(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["shift-col", str(simple_csv), str(out), "--column", "value", "--offset", "1"])
    assert "Rows shifted" in r.stdout
