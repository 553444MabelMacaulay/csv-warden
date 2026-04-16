"""CLI tests for the fill command."""
import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "score"])
        w.writerow(["Alice", "10"])
        w.writerow(["", ""])
    return p


def test_fill_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, [
        "fill", str(simple_csv), str(out),
        "--fill", "name=Unknown", "--fill", "score=0"
    ])
    assert result.exit_code == 0


def test_fill_output_replaces_missing(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, [
        "fill", str(simple_csv), str(out),
        "--fill", "name=Unknown", "--fill", "score=0"
    ])
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[1]["name"] == "Unknown"
    assert rows[1]["score"] == "0"


def test_fill_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, [
        "fill", "ghost.csv", str(out), "--fill", "a=b"
    ])
    assert result.exit_code == 1


def test_fill_forward_strategy(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, [
        "fill", str(simple_csv), str(out),
        "--fill", "name=x",
        "--strategy", "forward"
    ])
    assert result.exit_code == 0
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[1]["name"] == "Alice"
