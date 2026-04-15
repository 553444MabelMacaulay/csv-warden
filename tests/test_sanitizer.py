"""Tests for csv_warden.sanitizer."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from csv_warden.sanitizer import sanitize_csv, SanitizeResult


@pytest.fixture()
def tmp_csv(tmp_path: Path):
    """Return a factory that writes CSV text to a temp file."""
    def _write(content: str, name: str = "data.csv") -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p
    return _write


def test_strip_whitespace(tmp_csv):
    src = tmp_csv("""\
        name, age
        " Alice "," 30 "
        " Bob "," 25 "
    """)
    result = sanitize_csv(src, strip_whitespace=True)
    assert result.cells_modified > 0
    rows = list(csv.reader(src.open()))
    assert rows[1][0] == "Alice"
    assert rows[1][1] == "30"


def test_drop_empty_rows(tmp_csv):
    src = tmp_csv("""\
        name,age
        Alice,30
        ,
        Bob,25
    """)
    result = sanitize_csv(src, drop_empty_rows=True)
    assert result.rows_dropped == 1
    assert result.rows_written == 2


def test_no_drop_empty_rows(tmp_csv):
    src = tmp_csv("""\
        name,age
        Alice,30
        ,
    """)
    result = sanitize_csv(src, drop_empty_rows=False)
    assert result.rows_dropped == 0
    assert result.rows_written == 2


def test_extra_transform(tmp_csv):
    src = tmp_csv("""\
        name,age
        alice,30
        bob,25
    """)
    result = sanitize_csv(src, extra_transforms={"name": str.upper})
    rows = list(csv.reader(src.open()))
    assert rows[1][0] == "ALICE"
    assert result.cells_modified == 2


def test_write_to_separate_dest(tmp_csv, tmp_path):
    src = tmp_csv("""\
        name,age
        " Alice ",30
    """)
    dest = tmp_path / "out.csv"
    sanitize_csv(src, dest=dest)
    rows = list(csv.reader(dest.open()))
    assert rows[1][0] == "Alice"
    # Source should be unchanged
    original = list(csv.reader(src.open()))
    assert original[1][0] == " Alice "


def test_summary_contains_counts(tmp_csv):
    src = tmp_csv("""\
        name,age
        " Alice ",30
        ,
    """)
    result = sanitize_csv(src)
    summary = result.summary()
    assert "Rows read" in summary
    assert "Rows dropped" in summary
