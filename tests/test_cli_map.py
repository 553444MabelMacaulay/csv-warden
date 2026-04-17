import csv
import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with p.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "grade"])
        w.writerow(["Alice", "A"])
        w.writerow(["Bob", "B"])
        w.writerow(["Carol", "A"])
    return p


def test_map_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    mapping = json.dumps({"A": "Excellent", "B": "Good"})
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["map", str(simple_csv), str(out), "--column", "grade", "--mapping", mapping],
    )
    assert result.exit_code == 0


def test_map_output_replaces_values(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    mapping = json.dumps({"A": "Excellent", "B": "Good"})
    runner = CliRunner()
    runner.invoke(
        main,
        ["map", str(simple_csv), str(out), "--column", "grade", "--mapping", mapping],
    )
    with out.open() as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["grade"] == "Excellent"
    assert rows[1]["grade"] == "Good"


def test_map_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["map", str(tmp_path / "nope.csv"), str(out), "--column", "grade", "--mapping", '{"A":"X"}'],
    )
    assert result.exit_code == 1


def test_map_with_default(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    mapping = json.dumps({"A": "Excellent"})
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["map", str(simple_csv), str(out), "--column", "grade", "--mapping", mapping, "--default", "Other"],
    )
    assert result.exit_code == 0
    with out.open() as fh:
        rows = list(csv.DictReader(fh))
    assert rows[1]["grade"] == "Other"
