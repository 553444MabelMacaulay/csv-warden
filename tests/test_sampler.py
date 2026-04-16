import csv
import pytest
from pathlib import Path
from csv_warden.sampler import sample_csv, summary


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _make_rows(n):
    return [{"id": str(i), "value": str(i * 10)} for i in range(n)]


def test_sample_by_n(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(20))
    result = sample_csv(str(src), str(out), n=5, seed=42)
    assert result.sampled_rows == 5
    assert result.total_rows == 20
    assert len(_read(out)) == 5


def test_sample_by_fraction(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(100))
    result = sample_csv(str(src), str(out), fraction=0.1, seed=0)
    assert result.sampled_rows == 10


def test_sample_n_exceeds_rows(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(5))
    result = sample_csv(str(src), str(out), n=100, seed=1)
    assert result.sampled_rows == 5


def test_missing_file(tmp_csv):
    out = tmp_csv / "out.csv"
    result = sample_csv(str(tmp_csv / "nope.csv"), str(out), n=5)
    assert result.errors
    assert "not found" in result.errors[0]


def test_no_n_or_fraction(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(10))
    result = sample_csv(str(src), str(out))
    assert result.errors


def test_invalid_fraction(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(10))
    result = sample_csv(str(src), str(out), fraction=1.5)
    assert result.errors


def test_summary_contains_key_info(tmp_csv):
    src = tmp_csv / "input.csv"
    out = tmp_csv / "out.csv"
    _write(src, _make_rows(10))
    result = sample_csv(str(src), str(out), n=3, seed=7)
    s = summary(result)
    assert "Sampled rows" in s
    assert "3" in s
