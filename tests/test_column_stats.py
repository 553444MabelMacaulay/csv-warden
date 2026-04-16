"""Tests for csv_warden.column_stats."""
import pytest
from pathlib import Path
from csv_warden.column_stats import column_stats


@pytest.fixture
def tmp_csv(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_basic_numeric(tmp_csv):
    p = tmp_csv("data.csv", "a,b\n1,10\n2,20\n3,30\n")
    result = column_stats(p)
    assert result.success()
    assert "a" in result.columns
    assert result.columns["a"].min_val == 1.0
    assert result.columns["a"].max_val == 3.0
    assert result.columns["a"].mean == 2.0
    assert result.columns["b"].mean == 20.0


def test_missing_values(tmp_csv):
    p = tmp_csv("data.csv", "a\n1\n\n3\n")
    result = column_stats(p)
    assert result.columns["a"].missing == 1
    assert result.columns["a"].count == 3


def test_non_numeric_column_skipped(tmp_csv):
    p = tmp_csv("data.csv", "a,name\n1,alice\n2,bob\n")
    result = column_stats(p)
    assert "name" in result.skipped
    assert "a" in result.columns


def test_select_columns(tmp_csv):
    p = tmp_csv("data.csv", "a,b,c\n1,2,3\n4,5,6\n")
    result = column_stats(p, columns=["a", "c"])
    assert "b" not in result.columns
    assert "a" in result.columns
    assert "c" in result.columns


def test_file_not_found():
    result = column_stats("nonexistent.csv")
    assert not result.success()
    assert any("not found" in e for e in result.errors)


def test_summary_output(tmp_csv):
    p = tmp_csv("data.csv", "x\n10\n20\n30\n")
    result = column_stats(p)
    summary = result.summary()
    assert "x" in summary
    assert "mean" in summary


def test_stddev_single_value(tmp_csv):
    p = tmp_csv("data.csv", "a\n5\n")
    result = column_stats(p)
    assert result.columns["a"].stddev is None
    assert result.columns["a"].mean == 5.0
