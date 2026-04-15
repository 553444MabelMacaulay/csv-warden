"""CLI integration tests for the 'transform' sub-command."""

import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "score"])
        writer.writeheader()
        writer.writerows([
            {"name": "alice", "score": "95"},
            {"name": "bob",   "score": "80"},
        ])
    return str(p)


def test_transform_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(
        main, ["transform", simple_csv, out, "--col", "name=upper"]
    )
    assert result.exit_code == 0


def test_transform_output_uppercased(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    runner.invoke(main, ["transform", simple_csv, out, "--col", "name=upper"])
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] == "ALICE"
    assert rows[1]["name"] == "BOB"


def test_transform_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(
        main, ["transform", "ghost.csv", out, "--col", "x=lower"]
    )
    assert result.exit_code == 1


def test_transform_unknown_transform_exits_one(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(
        main, ["transform", simple_csv, out, "--col", "name=reverse"]
    )
    assert result.exit_code == 1


def test_transform_multiple_cols(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["transform", simple_csv, out,
         "--col", "name=upper", "--col", "score=strip"],
    )
    assert result.exit_code == 0
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] == "ALICE"
