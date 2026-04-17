"""CLI tests for the cast command."""
import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "score"])
        w.writeheader()
        w.writerows([{"name": "alice", "score": "9.5"}, {"name": "bob", "score": "7.0"}])
    return p


def test_cast_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["cast", str(simple_csv), str(out), "--cast", "score:float"])
    assert result.exit_code == 0


def test_cast_output_converts_column(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["cast", str(simple_csv), str(out), "--cast", "score:int"])
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["score"] == "9"
    assert rows[1]["score"] == "7"


def test_cast_missing_file_exits_one(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["cast", str(tmp_path / "nope.csv"), str(tmp_path / "out.csv"), "--cast", "x:int"])
    assert result.exit_code == 1


def test_cast_unsupported_type_exits_one(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["cast", str(simple_csv), str(out), "--cast", "score:datetime"])
    assert result.exit_code == 1


def test_cast_multiple_casts(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, [
        "cast", str(simple_csv), str(out),
        "--cast", "score:float",
        "--cast", "name:str",
    ])
    assert result.exit_code == 0
