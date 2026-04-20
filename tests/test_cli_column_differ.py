"""CLI integration tests for the differ-col sub-command."""
import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score_a,score_b\nAlice,10,8\nBob,5,5\nCarol,3,9\n")
    return p


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_differ_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    result = _run([
        "differ-col", str(simple_csv),
        "--col-a", "score_a",
        "--col-b", "score_b",
        "--output", str(out),
    ])
    assert result.exit_code == 0


def test_differ_col_flag_output(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "differ-col", str(simple_csv),
        "--col-a", "score_a",
        "--col-b", "score_b",
        "--output", str(out),
        "--mode", "flag",
    ])
    rows = list(csv.DictReader(out.open(newline="")))
    assert rows[0]["__diff__"] == "True"   # 10 != 8
    assert rows[1]["__diff__"] == "False"  # 5 == 5


def test_differ_col_delta_output(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "differ-col", str(simple_csv),
        "--col-a", "score_a",
        "--col-b", "score_b",
        "--output", str(out),
        "--mode", "delta",
    ])
    rows = list(csv.DictReader(out.open(newline="")))
    assert float(rows[0]["__diff__"]) == pytest.approx(2.0)
    assert float(rows[1]["__diff__"]) == pytest.approx(0.0)


def test_differ_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    result = _run([
        "differ-col", "no_file.csv",
        "--col-a", "a",
        "--col-b", "b",
        "--output", str(out),
    ])
    assert result.exit_code == 1


def test_differ_col_custom_diff_col_name(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run([
        "differ-col", str(simple_csv),
        "--col-a", "score_a",
        "--col-b", "score_b",
        "--output", str(out),
        "--diff-col", "changed",
    ])
    rows = list(csv.DictReader(out.open(newline="")))
    assert "changed" in rows[0]
