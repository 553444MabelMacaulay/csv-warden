"""CLI integration tests for the 'aggregate' sub-command."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nAlice,10\nBob,20\nCarol,30\n", encoding="utf-8")
    return str(p)


def test_aggregate_exit_zero(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", simple_csv, "score", "sum"])
    assert result.exit_code == 0


def test_aggregate_output_shows_result(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", simple_csv, "score", "sum"])
    assert "60" in result.output


def test_aggregate_mean(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", simple_csv, "score", "mean"])
    assert "20" in result.output


def test_aggregate_missing_file_exits_one():
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", "ghost.csv", "score", "sum"])
    assert result.exit_code == 1


def test_aggregate_unknown_func_exits_one(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", simple_csv, "score", "variance"])
    assert result.exit_code == 1


def test_aggregate_unknown_column_exits_one(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", simple_csv, "nonexistent", "sum"])
    assert result.exit_code == 1
