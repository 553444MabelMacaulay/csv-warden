"""Row filtering for CSV files based on column conditions."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FilterResult:
    input_path: str
    output_path: Optional[str]
    total_rows: int = 0
    kept_rows: int = 0
    dropped_rows: int = 0
    errors: list[str] = field(default_factory=list)


def summary(result: FilterResult) -> str:
    lines = [
        f"Input:        {result.input_path}",
        f"Output:       {result.output_path or '(none)'}",
        f"Total rows:   {result.total_rows}",
        f"Kept rows:    {result.kept_rows}",
        f"Dropped rows: {result.dropped_rows}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def filter_csv(
    input_path: str,
    output_path: Optional[str] = None,
    column: Optional[str] = None,
    value: Optional[str] = None,
    exclude: bool = False,
) -> FilterResult:
    """Filter rows where *column* equals *value*.

    Parameters
    ----------
    input_path:  source CSV file.
    output_path: destination CSV file (optional).
    column:      column name to match against.
    value:       value to match (string comparison).
    exclude:     when True, *drop* matching rows instead of keeping them.
    """
    result = FilterResult(input_path=input_path, output_path=output_path)

    path = Path(input_path)
    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if not column or value is None:
        result.errors.append("Both --column and --value are required for filtering.")
        return result

    try:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or column not in reader.fieldnames:
                result.errors.append(f"Column '{column}' not found in CSV.")
                return result
            rows = list(reader)
            fieldnames = list(reader.fieldnames)

        result.total_rows = len(rows)
        kept: list[dict] = []
        for row in rows:
            matches = row[column] == value
            keep = (not matches) if exclude else matches
            if keep:
                kept.append(row)

        result.kept_rows = len(kept)
        result.dropped_rows = result.total_rows - result.kept_rows

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(kept)

    except Exception as exc:  # pragma: no cover
        result.errors.append(str(exc))

    return result
