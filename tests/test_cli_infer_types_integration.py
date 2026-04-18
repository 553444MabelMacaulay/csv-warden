"""Integration tests: infer-types on varied data."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def mixed_csv(tmp_path):
    p = tmp_path / "mixed.csv"
    p.write_text(
        "id,active,joined,ratio\n"
        "1,true,2023-01-15,0.75\n"
        "2,false,2022-06-30,1.20\n",
        encoding="utf-8",
    )
    return p


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_warden", *args],
        capture_output=True,
        text=True,
    )


def test_all_four_types_detected(mixed_csv):
    r = _run("infer-types", str(mixed_csv))
    assert r.returncode == 0
    assert "int" in r.stdout
    assert "bool" in r.stdout
    assert "date" in r.stdout
    assert "float" in r.stdout


def test_summary_header_present(mixed_csv):
    r = _run("infer-types", str(mixed_csv))
    assert "Column Type Inference" in r.stdout


def test_columns_analysed_count(mixed_csv):
    r = _run("infer-types", str(mixed_csv))
    assert "4" in r.stdout
