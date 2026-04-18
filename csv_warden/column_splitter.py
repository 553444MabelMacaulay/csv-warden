"""Split a single column into multiple columns by a delimiter."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SplitColResult:
    input_file: str
    column: str
    delimiter: str
    new_columns: List[str] = field(default_factory=list)
    rows_processed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: SplitColResult) -> str:
    lines = [
        f"Input:        {result.input_file}",
        f"Column:       {result.column}",
        f"Delimiter:    {result.delimiter!r}",
        f"New columns:  {', '.join(result.new_columns)}",
        f"Rows:         {result.rows_processed}",
    ]
    if result.errors:
        lines.append(f"Errors:       {len(result.errors)}")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def split_column(
    input_path: str,
    output_path: str,
    column: str,
    delimiter: str,
    new_columns: Optional[List[str]] = None,
    drop_original: bool = False,
) -> SplitColResult:
    src = Path(input_path)
    result = SplitColResult(input_file=input_path, column=column, delimiter=delimiter)

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

    # Determine max parts to infer new column names if not provided
    split_values = [r[column].split(delimiter) for r in rows]
    max_parts = max((len(s) for s in split_values), default=0)

    if new_columns:
        col_names = list(new_columns)
        # Pad if needed
        for i in range(len(col_names), max_parts):
            col_names.append(f"{column}_{i}")
    else:
        col_names = [f"{column}_{i}" for i in range(max_parts)]

    result.new_columns = col_names

    insert_at = fieldnames.index(column)
    out_fields = list(fieldnames)
    for i, nc in enumerate(col_names):
        out_fields.insert(insert_at + 1 + i, nc)
    if drop_original:
        out_fields.remove(column)

    out_rows = []
    for row, parts in zip(rows, split_values):
        new_row = dict(row)
        for i, nc in enumerate(col_names):
            new_row[nc] = parts[i] if i < len(parts) else ""
        if drop_original:
            del new_row[column]
        out_rows.append(new_row)
        result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
