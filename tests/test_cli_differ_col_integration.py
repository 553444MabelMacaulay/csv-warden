"""Integration tests — differ-col summary output and round-trip correctness."""
import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture
def mixed_csv(tmp_path):
    p = tmp_path / "mixed.csv"
    p.write_text(
        "id,pred,actual\n"
        "1,0.9,0.9\n"
        "2,0.5,0.8\n"
        "3,1.0,0.0\n"
        "4,0.3,0.3\n"
    )
    return p


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_summary_shows_row_counts(mixed_csv, tmp_path):
    out = tmp_path / "out.csv"
    result = _run([
        "differ-col", str(mixed_csv),
        "--col-a", "pred",
        "--col-b", "actual",
        "--output", str(out),
    ])
    assert "4" in result.output   # rows total
    assert "2" in result.output   # rows different


def test_all_original_columns_preserved(mixed_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "differ-col", str(mixed_csv),
        "--col-a", "pred",
        "--col-b", "actual",
        "--output", str(out),
    ])
    rows = list(csv.DictReader(out.open(newline="")))
    assert "id" in rows[0]
    assert "pred" in rows[0]
    assert "actual" in rows[0]
    assert "__diff__" in rows[0]


def test_delta_sums_correctly(mixed_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "differ-col", str(mixed_csv),
        "--col-a", "pred",
        "--col-b", "actual",
        "--output", str(out),
        "--mode", "delta",
    ])
    rows = list(csv.DictReader(out.open(newline="")))
    total_delta = sum(float(r["__diff__"]) for r in rows)
    assert total_delta == pytest.approx((0.9 - 0.9) + (0.5 - 0.8) + (1.0 - 0.0) + (0.3 - 0.3))
