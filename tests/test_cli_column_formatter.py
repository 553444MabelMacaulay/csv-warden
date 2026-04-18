import csv
import pytest
from pathlib import Path
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,city\nalice,paris\nbob,london\n", encoding="utf-8")
    return p


def _run(args):
    from subprocess import run as sp_run, PIPE
    r = sp_run(["python", "-m", "csv_warden"] + args, stdout=PIPE, stderr=PIPE, text=True)
    return r


def test_format_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", str(simple_csv), str(out), "--fmt", "name:upper"])
    assert r.returncode == 0


def test_format_col_output_uppercased(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run(["format-col", str(simple_csv), str(out), "--fmt", "name:upper"])
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[0]["name"] == "ALICE"
    assert rows[1]["name"] == "BOB"


def test_format_col_multiple_formats(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", str(simple_csv), str(out), "--fmt", "name:title", "--fmt", "city:upper"])
    assert r.returncode == 0
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[0]["city"] == "PARIS"


def test_format_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", "ghost.csv", str(out), "--fmt", "name:upper"])
    assert r.returncode == 1


def test_format_col_bad_fmt_exits_one(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", str(simple_csv), str(out), "--fmt", "name_no_colon"])
    assert r.returncode == 1
