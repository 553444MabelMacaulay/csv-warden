"""column_shifter.py – shift numeric column values by a fixed offset or scale factor."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ShiftResult:
    input_file: str
    column: str
    rows_processed: int = 0
    rows_shifted: int = 0
    rows_skipped: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: ShiftResult) -> str:
    lines = [
        f"Input:          {result.input_file}",
        f"Column:         {result.column}",
        f"Rows processed: {result.rows_processed}",
        f"Rows shifted:   {result.rows_shifted}",
        f"Rows skipped:   {result.rows_skipped}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def shift_csv(
    input_path: str,
    output_path: str,
    column: str,
    offset: float = 0.0,
    scale: float = 1.0,
    suffix: Optional[str] = None,
) -> ShiftResult:
    """Apply ``value * scale + offset`` to every numeric cell in *column*.

    If *suffix* is given a new column ``<column><suffix>`` is added instead of
    overwriting the original.
    """
    src = Path(input_path)
    result = ShiftResult(input_file=input_path, column=column)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result

        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result

        out_col = f"{column}{suffix}" if suffix else column
        out_fields = fieldnames[:]
        if suffix and out_col not in out_fields:
            insert_at = out_fields.index(column) + 1
            out_fields.insert(insert_at, out_col)

        rows: List[dict] = []
        for row in reader:
            result.rows_processed += 1
            raw = row.get(column, "")
            try:
                new_val = float(raw) * scale + offset
                row[out_col] = f"{new_val:g}"
                result.rows_shifted += 1
            except (ValueError, TypeError):
                if suffix:
                    row[out_col] = ""
                result.rows_skipped += 1
            rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    return result
