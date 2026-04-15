"""Tests for csv_warden.aggregator."""
import pytest
from pathlib import Path
from csv_warden.aggregator import aggregate_csv, summary, SUPPORTED_FUNCS


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "data.csv"


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_sum(tmp_csv):
    _write(tmp_csv, "name,score\nAlice,10\nBob,20\nCarol,30\n")
    result = aggregate_csv(str(tmp_csv), "score", "sum")
    assert result.value == 60.0
    assert not result.errors


def test_mean(tmp_csv):
    _write(tmp_csv, "name,score\nAlice,10\nBob,30\n")
    result = aggregate_csv(str(tmp_csv), "score", "mean")
    assert result.value == 20.0


def test_min(tmp_csv):
    _write(tmp_csv, "x\n5\n2\n8\n")
    result = aggregate_csv(str(tmp_csv), "x", "min")
    assert result.value == 2.0


def test_max(tmp_csv):
    _write(tmp_csv, "x\n5\n2\n8\n")
    result = aggregate_csv(str(tmp_csv), "x", "max")
    assert result.value == 8.0


def test_count(tmp_csv):
    _write(tmp_csv, "x\n1\n2\n\n4\n")
    result = aggregate_csv(str(tmp_csv), "x", "count")
    assert result.value == 3.0
    assert result.warnings


def test_skips_non_numeric(tmp_csv):
    _write(tmp_csv, "x\n1\nfoo\n3\n")
    result = aggregate_csv(str(tmp_csv), "x", "sum")
    assert result.value == 4.0
    assert any("skipped" in w for w in result.warnings)


def test_missing_column(tmp_csv):
    _write(tmp_csv, "a,b\n1,2\n")
    result = aggregate_csv(str(tmp_csv), "z", "sum")
    assert result.errors
    assert result.value is None


def test_file_not_found():
    result = aggregate_csv("nonexistent.csv", "x", "sum")
    assert result.errors


def test_unsupported_func(tmp_csv):
    _write(tmp_csv, "x\n1\n")
    result = aggregate_csv(str(tmp_csv), "x", "median")
    assert result.errors
    assert "Unsupported" in result.errors[0]


def test_summary_contains_key_fields(tmp_csv):
    _write(tmp_csv, "score\n10\n20\n")
    result = aggregate_csv(str(tmp_csv), "score", "sum")
    out = summary(result)
    assert "sum" in out
    assert "30" in out
    assert "score" in out
