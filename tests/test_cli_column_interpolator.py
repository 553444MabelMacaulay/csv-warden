"""CLI tests for the interpolate-col sub-command."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("val\n1\n\n\n7\n", encoding="utf-8")
    return p


def _run(args, **kwargs):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden"] + args,
        capture_output=True,
        text=True,
        **kwargs,
    )


def test_interpolate_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["interpolate-col", str(simple_csv), str(out), "--column", "val"])
    assert r.returncode == 0


def test_interpolate_col_output_fills_gaps(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["interpolate-col", str(simple_csv), str(out), "--column", "val"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    # linear: 1, 3, 5, 7
    assert float(rows[1]["val"]) == pytest.approx(3.0)
    assert float(rows[2]["val"]) == pytest.approx(5.0)


def test_interpolate_col_forward_method(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["interpolate-col", str(simple_csv), str(out), "--column", "val", "--method", "forward"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[1]["val"] == "1.0"
    assert rows[2]["val"] == "1.0"


def test_interpolate_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["interpolate-col", str(tmp_path / "ghost.csv"), str(out), "--column", "val"])
    assert r.returncode == 1


def test_interpolate_col_summary_mentions_filled(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["interpolate-col", str(simple_csv), str(out), "--column", "val"])
    assert "Filled" in r.stdout
    assert "2" in r.stdout
