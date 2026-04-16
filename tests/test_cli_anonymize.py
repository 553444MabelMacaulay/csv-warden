"""CLI tests for the anonymize command."""
import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "score"])
        writer.writeheader()
        writer.writerows([{"name": "Alice", "score": "90"}, {"name": "Bob", "score": "80"}])
    return p


def test_anonymize_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["anonymize", str(simple_csv), str(out), "--columns", "name"])
    assert result.exit_code == 0


def test_anonymize_output_hashed(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["anonymize", str(simple_csv), str(out), "--columns", "name"])
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] not in ("Alice", "Bob")
    assert rows[0]["score"] == "90"


def test_anonymize_mask_flag(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["anonymize", str(simple_csv), str(out), "--columns", "name", "--mask"])
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert all(r["name"] == "***" for r in rows)


def test_anonymize_missing_file_exits_one(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["anonymize", "no.csv", str(tmp_path / "out.csv"), "--columns", "x"])
    assert result.exit_code == 1
