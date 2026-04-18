"""column_coalescer.py – fill missing values in a column from one or more fallback columns."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CoalesceResult:
    input_path: str
    output_path: str
    target_column: str
    fallback_columns: List[str]
    rows_filled: int = 0
    rows_total: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: CoalesceResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Target column   : {result.target_column}",
        f"Fallback columns: {', '.join(result.fallback_columns)}",
        f"Rows total : {result.rows_total}",
        f"Rows filled: {result.rows_filled}",
    ]
    if result.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in result.errors)
    return "\n".join(lines)


def _is_missing(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""


def coalesce_csv(
    input_path: str,
    output_path: str,
    target_column: str,
    fallback_columns: List[str],
) -> CoalesceResult:
    result = CoalesceResult(
        input_path=input_path,
        output_path=output_path,
        target_column=target_column,
        fallback_columns=fallback_columns,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no headers.")
            return result
        fieldnames = list(reader.fieldnames)
        if target_column not in fieldnames:
            result.errors.append(f"Target column '{target_column}' not found.")
            return result
        missing_fb = [c for c in fallback_columns if c not in fieldnames]
        if missing_fb:
            result.errors.append(f"Fallback columns not found: {missing_fb}")
            return result
        rows = list(reader)

    out_rows = []
    for row in rows:
        result.rows_total += 1
        if _is_missing(row.get(target_column)):
            for fb in fallback_columns:
                if not _is_missing(row.get(fb)):
                    row[target_column] = row[fb]
                    result.rows_filled += 1
                    break
        out_rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
