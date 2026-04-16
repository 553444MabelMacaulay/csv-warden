"""CLI tests for the schema-validate command."""
import json
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,score\nAlice,30,9.5\nBob,25,8.0\n", encoding="utf-8")
    return str(p)


def test_schema_exit_zero(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["schema", simple_csv, "--col", "age:int", "--col", "score:float"])
    assert result.exit_code == 0


def test_schema_output_pass(simple_csv):
    runner = CliRunner()
    result = runner.invoke(main, ["schema", simple_csv, "--col", "age:int"])
    assert "PASS" in result.output


def test_schema_invalid_exits_one(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("age\nnotanumber\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["schema", str(p), "--col", "age:int"])
    assert result.exit_code == 1
    assert "FAIL" in result.output


def test_schema_missing_file_exits_one():
    runner = CliRunner()
    result = runner.invoke(main, ["schema", "ghost.csv", "--col", "x:int"])
    assert result.exit_code == 1


def test_schema_required_flag(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name\nAlice\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["schema", str(p), "--required", "age"])
    assert result.exit_code == 1
    assert "age" in result.output
