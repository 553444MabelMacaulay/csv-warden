"""Integration tests for the `profile` CLI command."""

from __future__ import annotations

import csv
import pytest
from pathlib import Path

from csv_warden.cli import main


@pytest.fixture()
def simple_csv(tmp_path: Path) -> str:
    p = tmp_path / "data.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "score"])
        w.writerow(["Alice", "95"])
        w.writerow(["Bob", ""])
        w.writerow(["Carol", "87"])
    return str(p)


def test_profile_exit_zero(simple_csv):
    assert main(["profile", simple_csv]) == 0


def test_profile_output_contains_columns(simple_csv, capsys):
    main(["profile", simple_csv])
    out = capsys.readouterr().out
    assert "name" in out
    assert "score" in out


def test_profile_output_row_count(simple_csv, capsys):
    main(["profile", simple_csv])
    out = capsys.readouterr().out
    assert "3" in out  # 3 data rows


def test_profile_missing_file_exits_one(tmp_path):
    rc = main(["profile", str(tmp_path / "ghost.csv")])
    assert rc == 1


def test_profile_top_n_flag(simple_csv):
    """--top-n should not raise and still return 0."""
    assert main(["profile", "--top-n", "3", simple_csv]) == 0


def test_validate_command_still_works(simple_csv):
    """Ensure validate command is unaffected after CLI refactor."""
    rc = main(["validate", simple_csv])
    assert rc in (0, 1)  # valid or warnings — just must not crash
