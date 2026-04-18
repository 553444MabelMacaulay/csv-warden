import csv
import pytest
from click.testing import CliRunner
from pathlib import Path
import subprocess
import sys


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "city"])
        writer.writeheader()
        writer.writerows([
            {"name": "Hello World", "city": "new york"},
            {"name": "Foo-Bar", "city": "los angeles"},
        ])
    return p


def run_cmd(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden"] + list(args),
        capture_output=True,
        text=True,
    )


def test_normalize_col_exit_zero(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = run_cmd("normalize-col", str(simple_csv), str(out), "--columns", "name")
    assert r.returncode == 0


def test_normalize_col_snake_case(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    run_cmd("normalize-col", str(simple_csv), str(out), "--columns", "name", "--mode", "snake_case")
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["name"] == "hello_world"
    assert rows[1]["name"] == "foo_bar"
    assert rows[0]["city"] == "new york"  # untouched


def test_normalize_col_upper(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    run_cmd("normalize-col", str(simple_csv), str(out), "--columns", "city", "--mode", "upper")
    with open(out, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["city"] == "NEW YORK"


def test_normalize_col_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.csv"
    r = run_cmd("normalize-col", str(tmp_path / "no.csv"), str(out), "--columns", "name")
    assert r.returncode == 1


def test_normalize_col_output_mentions_columns(simple_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = run_cmd("normalize-col", str(simple_csv), str(out), "--columns", "name,city")
    assert "name" in r.stdout
    assert "city" in r.stdout
