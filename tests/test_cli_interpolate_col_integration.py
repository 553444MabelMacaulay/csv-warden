"""Integration tests for interpolate-col covering multi-column CSVs."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def multi_col_csv(tmp_path):
    p = tmp_path / "multi.csv"
    rows = [
        "id,score,label",
        "1,10,a",
        "2,,b",
        "3,,c",
        "4,40,d",
    ]
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return p


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden"] + args,
        capture_output=True,
        text=True,
    )


def test_all_original_columns_preserved(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["interpolate-col", str(multi_col_csv), str(out), "--column", "score"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert "id" in rows[0]
    assert "label" in rows[0]
    assert "score" in rows[0]


def test_non_target_column_untouched(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["interpolate-col", str(multi_col_csv), str(out), "--column", "score"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    labels = [r["label"] for r in rows]
    assert labels == ["a", "b", "c", "d"]


def test_linear_values_correct(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["interpolate-col", str(multi_col_csv), str(out), "--column", "score"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert float(rows[1]["score"]) == pytest.approx(20.0)
    assert float(rows[2]["score"]) == pytest.approx(30.0)


def test_summary_mentions_method(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["interpolate-col", str(multi_col_csv), str(out), "--column", "score", "--method", "forward"])
    assert "forward" in r.stdout
