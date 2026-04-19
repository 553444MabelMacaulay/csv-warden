"""Stack (unpivot) multiple columns into a single key-value pair of columns."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class StackResult:
    input_path: str
    output_path: str
    columns_stacked: List[str] = field(default_factory=list)
    rows_in: int = 0
    rows_out: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: StackResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Columns stacked : {', '.join(result.columns_stacked)}",
        f"Rows in : {result.rows_in}",
        f"Rows out: {result.rows_out}",
    ]
    if result.errors:
        lines.append(f"Errors ({len(result.errors)}):")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def stack_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
    key_col: str = "key",
    value_col: str = "value",
    id_columns: Optional[List[str]] = None,
) -> StackResult:
    src = Path(input_path)
    result = StackResult(input_path=input_path, output_path=output_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    result.rows_in = len(rows)

    missing = [c for c in columns if c not in fieldnames]
    if missing:
        result.errors.append(f"Columns not found: {', '.join(missing)}")
        return result

    id_cols = id_columns if id_columns else [c for c in fieldnames if c not in columns]
    result.columns_stacked = columns

    out_fields = id_cols + [key_col, value_col]
    stacked: List[dict] = []
    for row in rows:
        base = {c: row[c] for c in id_cols if c in row}
        for col in columns:
            stacked.append({**base, key_col: col, value_col: row.get(col, "")})

    result.rows_out = len(stacked)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(stacked)

    return result
