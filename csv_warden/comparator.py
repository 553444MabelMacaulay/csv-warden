"""comparator.py — Compare two CSV files and report differences."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CompareResult:
    file_a: str
    file_b: str
    rows_only_in_a: int = 0
    rows_only_in_b: int = 0
    rows_in_common: int = 0
    column_mismatch: bool = False
    columns_a: List[str] = field(default_factory=list)
    columns_b: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def summary(result: CompareResult) -> str:
    """Return a human-readable summary of the comparison."""
    lines = [
        f"Comparing: {result.file_a}  vs  {result.file_b}",
    ]
    if result.errors:
        for e in result.errors:
            lines.append(f"  ERROR: {e}")
        return "\n".join(lines)

    if result.column_mismatch:
        lines.append(f"  Column mismatch!")
        lines.append(f"    {result.file_a} columns: {result.columns_a}")
        lines.append(f"    {result.file_b} columns: {result.columns_b}")
    else:
        lines.append(f"  Columns match: {result.columns_a}")

    lines.append(f"  Rows only in A : {result.rows_only_in_a}")
    lines.append(f"  Rows only in B : {result.rows_only_in_b}")
    lines.append(f"  Rows in common : {result.rows_in_common}")
    return "\n".join(lines)


def _read_rows(path: Path) -> tuple[List[str], List[tuple]]:
    """Read a CSV and return (headers, list-of-row-tuples)."""
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        headers = list(reader.fieldnames or [])
        rows = [tuple(row[h] for h in headers) for row in reader]
    return headers, rows


def compare_csv(
    file_a: str,
    file_b: str,
    key_column: Optional[str] = None,
) -> CompareResult:
    """Compare two CSV files row-by-row (or by key column).

    Parameters
    ----------
    file_a, file_b:
        Paths to the two CSV files to compare.
    key_column:
        Optional column name to use as a unique key.  When provided the
        comparison is key-based; otherwise full-row equality is used.
    """
    result = CompareResult(file_a=file_a, file_b=file_b)

    path_a, path_b = Path(file_a), Path(file_b)
    for label, p in (("A", path_a), ("B", path_b)):
        if not p.exists():
            result.errors.append(f"File {label} not found: {p}")
    if result.errors:
        return result

    headers_a, rows_a = _read_rows(path_a)
    headers_b, rows_b = _read_rows(path_b)

    result.columns_a = headers_a
    result.columns_b = headers_b

    if headers_a != headers_b:
        result.column_mismatch = True
        # Still attempt row comparison when key column exists in both
        if key_column and key_column not in headers_a:
            result.errors.append(f"Key column '{key_column}' not in {file_a}")
            return result
        if key_column and key_column not in headers_b:
            result.errors.append(f"Key column '{key_column}' not in {file_b}")
            return result

    if key_column:
        idx_a = headers_a.index(key_column)
        idx_b = headers_b.index(key_column)
        set_a = {row[idx_a] for row in rows_a}
        set_b = {row[idx_b] for row in rows_b}
    else:
        set_a = set(rows_a)
        set_b = set(rows_b)

    result.rows_only_in_a = len(set_a - set_b)
    result.rows_only_in_b = len(set_b - set_a)
    result.rows_in_common = len(set_a & set_b)
    return result
