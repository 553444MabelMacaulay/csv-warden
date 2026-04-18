"""Trim column values to a maximum character length."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TrimResult:
    input_path: str
    output_path: str
    columns: Dict[str, int]  # column -> max_length
    rows_processed: int = 0
    cells_trimmed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: TrimResult) -> str:
    lines = [
        f"Input:          {result.input_path}",
        f"Output:         {result.output_path}",
        f"Rows processed: {result.rows_processed}",
        f"Cells trimmed:  {result.cells_trimmed}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def trim_csv(
    input_path: str,
    output_path: str,
    columns: Dict[str, int],
    ellipsis_str: Optional[str] = None,
) -> TrimResult:
    """Trim specified columns to max_length characters.

    Args:
        input_path: Source CSV file.
        output_path: Destination CSV file.
        columns: Mapping of column name to max character length.
        ellipsis_str: Optional suffix appended when a value is trimmed (e.g. '...').
    """
    result = TrimResult(
        input_path=input_path,
        output_path=output_path,
        columns=columns,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("File is empty or has no header.")
            return result

        unknown = set(columns) - set(reader.fieldnames)
        if unknown:
            for col in sorted(unknown):
                result.errors.append(f"Column not found: {col}")
            return result

        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    out_rows = []
    for row in rows:
        result.rows_processed += 1
        new_row = dict(row)
        for col, max_len in columns.items():
            val = new_row.get(col, "") or ""
            if len(val) > max_len:
                trimmed = val[:max_len]
                if ellipsis_str:
                    trimmed = trimmed[: max(0, max_len - len(ellipsis_str))] + ellipsis_str
                new_row[col] = trimmed
                result.cells_trimmed += 1
        out_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
