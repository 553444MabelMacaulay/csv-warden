import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "subject", "score"])
        w.writerow(["Alice", "math", "90"])
        w.writerow(["Alice", "english", "85"])
        w.writerow(["Bob", "math", "70"])
        w.writerow(["Bob", "english", "80"])
    return str(p)


def test_pivot_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["pivot", simple_csv, out, "name", "subject", "score"])
    assert result.exit_code == 0


def test_pivot_output_has_pivot_columns(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    runner.invoke(main, ["pivot", simple_csv, out, "name", "subject", "score"])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        assert "math" in reader.fieldnames
        assert "english" in reader.fieldnames


def test_pivot_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["pivot", "no_file.csv", out, "a", "b", "c"])
    assert result.exit_code == 1


def test_pivot_aggfunc_sum(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["pivot", simple_csv, out, "name", "subject", "score", "--aggfunc", "sum"])
    assert result.exit_code == 0
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    alice = next(r for r in rows if r["name"] == "Alice")
    assert alice["math"] == "90.0"
