"""CLI tests for the smooth-col command."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "value"])
        w.writeheader()
        for i, v in enumerate([2, 4, 6, 8, 10], start=1):
            w.writerow({"id": str(i), "value": str(v)})
    return p


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden"] + args,
        capture_output=True,
        text=True,
    )


def test_smooth_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["smooth-col", str(simple_csv), str(out), "--column", "value"])
    assert r.returncode == 0


def test_smooth_col_output_written(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["smooth-col", str(simple_csv), str(out), "--column", "value"])
    assert out.exists()
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5
    assert "value" in rows[0]


def test_smooth_col_gaussian_method(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(
        [
            "smooth-col",
            str(simple_csv),
            str(out),
            "--column",
            "value",
            "--method",
            "gaussian",
            "--window",
            "2",
        ]
    )
    assert r.returncode == 0
    assert "gaussian" in r.stdout


def test_smooth_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["smooth-col", str(tmp_path / "nope.csv"), str(out), "--column", "value"])
    assert r.returncode == 1


def test_smooth_col_summary_shows_column(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["smooth-col", str(simple_csv), str(out), "--column", "value"])
    assert "value" in r.stdout
    assert "Smoothed rows" in r.stdout
