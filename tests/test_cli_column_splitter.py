import csv
import pytest
from click.testing import CliRunner
from csv_warden.cli import main


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["full_name", "score"])
        w.writeheader()
        w.writerows([{"full_name": "Alice Smith", "score": "90"},
                     {"full_name": "Bob Jones", "score": "80"}])
    return str(p)


def test_split_col_exit_zero(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["split-col", simple_csv, out, "--column", "full_name", "--delimiter", " "])
    assert result.exit_code == 0


def test_split_col_output_has_new_columns(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    runner.invoke(main, ["split-col", simple_csv, out, "--column", "full_name", "--delimiter", " "])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert "full_name_0" in rows[0]
    assert rows[0]["full_name_0"] == "Alice"
    assert rows[0]["full_name_1"] == "Smith"


def test_split_col_missing_file_exits_one(tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    result = runner.invoke(main, ["split-col", "ghost.csv", out, "--column", "x", "--delimiter", ","])
    assert result.exit_code == 1


def test_split_col_drop_original(simple_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    runner = CliRunner()
    runner.invoke(main, ["split-col", simple_csv, out, "--column", "full_name", "--delimiter", " ", "--drop-original"])
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert "full_name" not in rows[0]
