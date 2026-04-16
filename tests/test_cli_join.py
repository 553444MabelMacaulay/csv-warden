import pytest
from click.testing import CliRunner
from csv_warden.cli import main
import csv
from pathlib import Path


@pytest.fixture
def two_csvs(tmp_path):
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    left.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    right.write_text("id,score\n1,90\n2,85\n")
    return left, right, tmp_path


def test_join_exit_zero(two_csvs, tmp_path):
    left, right, d = two_csvs
    out = d / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["join", str(left), str(right), "--key", "id", "--output", str(out)])
    assert result.exit_code == 0


def test_join_output_inner(two_csvs, tmp_path):
    left, right, d = two_csvs
    out = d / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["join", str(left), str(right), "--key", "id", "--output", str(out)])
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 2
    assert "score" in rows[0]


def test_join_left_type(two_csvs, tmp_path):
    left, right, d = two_csvs
    out = d / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["join", str(left), str(right), "--key", "id", "--output", str(out), "--join-type", "left"])
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 3


def test_join_missing_file_exits_one(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.csv"
    result = runner.invoke(main, ["join", str(tmp_path / "nope.csv"), str(tmp_path / "also.csv"), "--key", "id", "--output", str(out)])
    assert result.exit_code == 1


def test_join_output_shows_rows(two_csvs, tmp_path):
    left, right, d = two_csvs
    out = d / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["join", str(left), str(right), "--key", "id", "--output", str(out)])
    assert "Output rows" in result.output
