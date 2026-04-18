"""Integration: duplicate-col round-trip preserves all original data."""
import csv
import pytest
from subprocess import run
from pathlib import Path


@pytest.fixture
def multi_col_csv(tmp_path):
    p = tmp_path / "multi.csv"
    p.write_text("id,first,last\n1,Alice,Smith\n2,Bob,Jones\n")
    return p


def test_round_trip_all_original_columns_present(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = run(
        ["python", "-m", "csv_warden", "duplicate-col", str(multi_col_csv), str(out),
         "--map", "first:first_dup", "--map", "last:last_dup"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    rows = list(csv.DictReader(open(out)))
    assert set(rows[0].keys()) == {"id", "first", "last", "first_dup", "last_dup"}
    assert rows[0]["first_dup"] == rows[0]["first"]
    assert rows[1]["last_dup"] == rows[1]["last"]


def test_summary_output_mentions_mapping(multi_col_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = run(
        ["python", "-m", "csv_warden", "duplicate-col", str(multi_col_csv), str(out),
         "--map", "id:id_copy"],
        capture_output=True, text=True,
    )
    assert "id->id_copy" in r.stdout
