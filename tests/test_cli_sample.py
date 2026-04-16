import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "name"])
        writer.writeheader()
        for i in range(20):
            writer.writerow({"id": str(i), "name": f"user{i}"})
    return p


def test_sample_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["sample", str(simple_csv), str(out), "--n", "5"])
    assert result.exit_code == 0


def test_sample_output_row_count(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["sample", str(simple_csv), str(out), "--n", "7", "--seed", "1"])
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 7


def test_sample_fraction(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["sample", str(simple_csv), str(out), "--fraction", "0.5", "--seed", "0"])
    assert result.exit_code == 0
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 10


def test_sample_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["sample", str(tmp_path / "ghost.csv"), str(out), "--n", "5"])
    assert result.exit_code == 1
