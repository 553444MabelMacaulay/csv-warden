"""Compute row-by-row diff between two columns in a CSV file."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class DiffResult:
    input_path: str
    col_a: str
    col_b: str
    output_path: str
    rows_total: int = 0
    rows_different: int = 0
    rows_same: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: DiffResult) -> str:
    lines = [
        f"Column Diff: '{result.col_a}' vs '{result.col_b}' in {result.input_path}",
        f"  Rows total    : {result.rows_total}",
        f"  Rows same     : {result.rows_same}",
        f"  Rows different: {result.rows_different}",
        f"  Output        : {result.output_path}",
    ]
    if result.errors:
        lines.append("  Errors:")
        for e in result.errors:
            lines.append(f"    - {e}")
    return "\n".join(lines)


def diff_columns(
    input_path: str,
    col_a: str,
    col_b: str,
    output_path: str,
    diff_col: str = "__diff__",
    mode: str = "flag",          # "flag" | "delta"
) -> DiffResult:
    """Compare two columns row-by-row and write result with a diff column.

    mode='flag'  -> diff column is 'True'/'False' (values differ / same)
    mode='delta' -> diff column is numeric difference (col_a - col_b); non-
                    numeric rows get empty string.
    """
    result = DiffResult(
        input_path=input_path,
        col_a=col_a,
        col_b=col_b,
        output_path=output_path,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if mode not in ("flag", "delta"):
        result.errors.append(f"Unknown mode '{mode}'. Use 'flag' or 'delta'.")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no headers.")
            return result
        fieldnames = list(reader.fieldnames)
        for col in (col_a, col_b):
            if col not in fieldnames:
                result.errors.append(f"Column '{col}' not found.")
        if result.errors:
            return result

        out_fields = fieldnames + [diff_col]
        rows_out: list = []

        for row in reader:
            result.rows_total += 1
            va, vb = row[col_a], row[col_b]
            if mode == "flag":
                different = va != vb
                row[diff_col] = str(different)
            else:  # delta
                try:
                    row[diff_col] = str(float(va) - float(vb))
                except (ValueError, TypeError):
                    row[diff_col] = ""
                different = va != vb
            if different:
                result.rows_different += 1
            else:
                result.rows_same += 1
            rows_out.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    return result
