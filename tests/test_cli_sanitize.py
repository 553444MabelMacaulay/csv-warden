"""CLI integration tests for the 'sanitize' sub-command."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from csv_warden.cli import main


@pytest.fixture()
def simple_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
            name,age
            " Alice "," 30 "
            ,
            Bob,25
        """),
        encoding="utf-8",
    )
    return p


def test_sanitize_exit_zero(simple_csv):
    assert main(["sanitize", str(simple_csv)]) == 0


def test_sanitize_strips_whitespace(simple_csv):
    main(["sanitize", str(simple_csv)])
    rows = list(csv.reader(simple_csv.open()))
    assert rows[1][0] == "Alice"
    assert rows[1][1] == "30"


def test_sanitize_drops_empty_rows(simple_csv):
    main(["sanitize", str(simple_csv)])
    rows = list(csv.reader(simple_csv.open()))
    # header + Alice + Bob = 3 rows (empty row dropped)
    assert len(rows) == 3


def test_sanitize_keep_empty_rows(simple_csv):
    main(["sanitize", str(simple_csv), "--keep-empty-rows"])
    rows = list(csv.reader(simple_csv.open()))
    assert len(rows) == 4


def test_sanitize_output_flag(simple_csv, tmp_path):
    dest = tmp_path / "out.csv"
    main(["sanitize", str(simple_csv), "--output", str(dest)])
    assert dest.exists()
    rows = list(csv.reader(dest.open()))
    assert rows[1][0] == "Alice"


def test_sanitize_missing_file_exits_one(tmp_path):
    missing = str(tmp_path / "ghost.csv")
    assert main(["sanitize", missing]) == 1


def test_sanitize_summary_output(simple_csv, capsys):
    main(["sanitize", str(simple_csv)])
    captured = capsys.readouterr()
    assert "Rows read" in captured.out
    assert "Rows dropped" in captured.out
