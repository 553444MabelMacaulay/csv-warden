"""Drop duplicate values within a column, replacing repeats with empty string or a fill value."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DedupeColResult:
    input_path: str
    output_path: str
    column: str
    rows_processed: int = 0
    cells_cleared: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: DedupeColResult) -> str:
    lines = [
        f"Column deduplication: {r.input_path} -> {r.output_path}",
        f"  Column   : {r.column}",
        f"  Rows     : {r.rows_processed}",
        f"  Cleared  : {r.cells_cleared}",
    ]
    if r.errors:
        lines.append(f"  Errors   : {len(r.errors)}")
        for e in r.errors:
            lines.append(f"    - {e}")
    return "\n".join(lines)


def dedupe_column(
    input_path: str,
    output_path: str,
    column: str,
    fill: str = "",
) -> DedupeColResult:
    result = DedupeColResult(input_path=input_path, output_path=output_path, column=column)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable CSV.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    last_seen: Optional[str] = None
    out_rows = []
    for row in rows:
        result.rows_processed += 1
        val = row[column]
        if val == last_seen:
            row[column] = fill
            result.cells_cleared += 1
        else:
            last_seen = val
        out_rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
