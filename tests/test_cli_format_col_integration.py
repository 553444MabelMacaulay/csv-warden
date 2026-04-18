import csv
import pytest
from pathlib import Path
from subprocess import run, PIPE


@pytest.fixture
def multi_row_csv(tmp_path):
    p = tmp_path / "data.csv"
    rows = "name,role\n  alice  ,developer\nBOB,MANAGER\ncathy,designer\n"
    p.write_text(rows, encoding="utf-8")
    return p


def _run(args):
    return run(["python", "-m", "csv_warden"] + args, stdout=PIPE, stderr=PIPE, text=True)


def test_strip_then_title(multi_row_csv, tmp_path):
    mid = tmp_path / "mid.csv"
    out = tmp_path / "out.csv"
    r1 = _run(["format-col", str(multi_row_csv), str(mid), "--fmt", "name:strip"])
    assert r1.returncode == 0
    r2 = _run(["format-col", str(mid), str(out), "--fmt", "name:title"])
    assert r2.returncode == 0
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert rows[0]["name"] == "Alice"


def test_summary_mentions_columns(multi_row_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", str(multi_row_csv), str(out), "--fmt", "role:lower"])
    assert "role" in r.stdout


def test_rows_affected_count(multi_row_csv, tmp_path):
    out = tmp_path / "out.csv"
    r = _run(["format-col", str(multi_row_csv), str(out), "--fmt", "role:lower"])
    assert "Rows affected" in r.stdout
