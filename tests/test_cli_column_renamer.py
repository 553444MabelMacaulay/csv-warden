import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "score"])
        writer.writeheader()
        writer.writerow({"name": "Alice", "score": "95"})
    return str(p)


def test_prefix_suffix_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["prefix-suffix", simple_csv, out, "--prefix", "p_"])
    assert result.exit_code == 0


def test_prefix_suffix_output_has_new_headers(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    runner.invoke(main, ["prefix-suffix", simple_csv, out, "--prefix", "col_"])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
    assert "col_name" in fields
    assert "col_score" in fields


def test_prefix_suffix_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["prefix-suffix", "ghost.csv", out, "--prefix", "x_"])
    assert result.exit_code == 1


def test_prefix_suffix_no_prefix_or_suffix_exits_one(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["prefix-suffix", simple_csv, out])
    assert result.exit_code == 1


def test_suffix_only(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["prefix-suffix", simple_csv, out, "--suffix", "_raw"])
    assert result.exit_code == 0
    with open(out, newline="") as f:
        fields = csv.DictReader(f).fieldnames
    assert "name_raw" in fields
