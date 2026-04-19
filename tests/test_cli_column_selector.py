import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "age", "city"])
        w.writeheader()
        w.writerows([
            {"name": "Alice", "age": "30", "city": "NY"},
            {"name": "Bob", "age": "25", "city": "LA"},
        ])
    return p


def test_select_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["select", str(simple_csv), str(out), "--columns", "name,age"])
    assert result.exit_code == 0


def test_select_output_has_only_selected_columns(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["select", str(simple_csv), str(out), "--columns", "name"])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert all("name" in r and "age" not in r and "city" not in r for r in rows)


def test_select_missing_file_exits_one(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["select", str(tmp_path / "ghost.csv"), str(tmp_path / "out.csv"), "--columns", "a"])
    assert result.exit_code == 1


def test_select_all_columns_missing_exits_one(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(main, ["select", str(simple_csv), str(out), "--columns", "zzz"])
    assert result.exit_code == 1


def test_select_multiple_columns_preserves_row_count(simple_csv, tmp_path):
    """Selecting multiple valid columns should preserve all rows from the source."""
    out = tmp_path / "out.csv"
    runner = CliRunner()
    runner.invoke(main, ["select", str(simple_csv), str(out), "--columns", "name,city"])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2
    assert all("name" in r and "city" in r and "age" not in r for r in rows)
