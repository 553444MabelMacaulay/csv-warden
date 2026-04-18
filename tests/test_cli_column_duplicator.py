import csv
import pytest
from click.testing import CliRunner
from pathlib import Path
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nAlice,90\nBob,80\n")
    return p


def test_duplicate_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    from subprocess import run, PIPE
    r = run(
        ["python", "-m", "csv_warden", "duplicate-col", str(simple_csv), str(out), "--map", "name:name2"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0


def test_duplicate_col_output_has_new_column(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    from subprocess import run
    run(
        ["python", "-m", "csv_warden", "duplicate-col", str(simple_csv), str(out), "--map", "name:name_copy"],
        capture_output=True,
    )
    rows = list(csv.DictReader(open(out)))
    assert rows[0]["name_copy"] == "Alice"


def test_duplicate_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    from subprocess import run
    r = run(
        ["python", "-m", "csv_warden", "duplicate-col", "no_file.csv", str(out), "--map", "a:b"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1


def test_duplicate_col_bad_map_format_exits_one(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    from subprocess import run
    r = run(
        ["python", "-m", "csv_warden", "duplicate-col", str(simple_csv), str(out), "--map", "namename2"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
