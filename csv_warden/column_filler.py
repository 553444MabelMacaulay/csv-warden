"""Fill missing values in CSV columns."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class FillResult:
    input_file: str
    output_file: str
    fills: Dict[str, int] = field(default_factory=dict)
    rows_processed: int = 0
    errors: list = field(default_factory=list)


def summary(result: FillResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file}",
        f"Rows processed: {result.rows_processed}",
    ]
    for col, count in result.fills.items():
        lines.append(f"  '{col}': {count} value(s) filled")
    if not result.fills:
        lines.append("  No missing values filled.")
    if result.errors:
        for e in result.errors:
            lines.append(f"  ERROR: {e}")
    return "\n".join(lines)


def _is_missing(value: Optional[str]) -> bool:
    """Return True if a cell value should be considered missing."""
    return value is None or value.strip() == ""


def fill_csv(
    input_path: str,
    output_path: str,
    fill_values: Dict[str, str],
    strategy: Optional[str] = None,
) -> FillResult:
    """Fill missing values in specified columns.

    Args:
        fill_values: mapping of column -> fill value (used when strategy is None or 'value').
        strategy: 'value' (default), 'forward', or 'empty' (fill with empty string).
    """
    result = FillResult(input_file=input_path, output_file=output_path)
    src = Path(input_path)
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

    result.rows_processed = len(rows)
    prev: Dict[str, str] = {}
    filled_rows = []
    for row in rows:
        new_row = dict(row)
        for col in fill_values if strategy != "empty" else fieldnames:
            val = new_row.get(col, "")
            if _is_missing(val):
                if strategy == "forward":
                    new_val = prev.get(col, "")
                elif strategy == "empty":
                    new_val = ""
                else:
                    new_val = fill_values.get(col, "")
                if new_val != val:
                    result.fills[col] = result.fills.get(col, 0) + 1
                new_row[col] = new_val
            prev[col] = new_row.get(col, "")
        filled_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filled_rows)

    return result
