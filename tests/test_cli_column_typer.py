"""CLI tests for the infer-types command."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def simple_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,score\nAlice,30,9.5\nBob,25,8.0\n", encoding="utf-8")
    return p


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden", *args],
        capture_output=True,
        text=True,
    )


def test_infer_types_exit_zero(simple_csv):
    r = _run("infer-types", str(simple_csv))
    assert r.returncode == 0


def test_infer_types_output_contains_columns(simple_csv):
    r = _run("infer-types", str(simple_csv))
    assert "name" in r.stdout
    assert "age" in r.stdout
    assert "score" in r.stdout


def test_infer_types_shows_inferred_types(simple_csv):
    r = _run("infer-types", str(simple_csv))
    assert "int" in r.stdout
    assert "float" in r.stdout
    assert "string" in r.stdout


def test_infer_types_missing_file_exits_one():
    r = _run("infer-types", "no_such_file.csv")
    assert r.returncode == 1


def test_infer_types_sample_flag(simple_csv):
    r = _run("infer-types", str(simple_csv), "--sample", "1")
    assert r.returncode == 0
    assert "age" in r.stdout
