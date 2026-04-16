"""Anonymize sensitive columns in a CSV file."""
from __future__ import annotations
import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class AnonymizeResult:
    input_file: str
    output_file: str
    columns: List[str]
    rows_processed: int = 0
    columns_not_found: List[str] = field(default_factory=list)
    error: Optional[str] = None


def summary(result: AnonymizeResult) -> str:
    lines = [
        f"Input:            {result.input_file}",
        f"Output:           {result.output_file}",
        f"Rows processed:   {result.rows_processed}",
        f"Columns hashed:   {', '.join(result.columns) or 'none'}",
    ]
    if result.columns_not_found:
        lines.append(f"Columns missing:  {', '.join(result.columns_not_found)}")
    if result.error:
        lines.append(f"Error:            {result.error}")
    return "\n".join(lines)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def anonymize_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
    mask: bool = False,
) -> AnonymizeResult:
    src = Path(input_path)
    result = AnonymizeResult(input_file=input_path, output_file=output_path, columns=columns)

    if not src.exists():
        result.error = f"File not found: {input_path}"
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.error = "Empty or header-less file"
            return result
        headers = list(reader.fieldnames)
        result.columns_not_found = [c for c in columns if c not in headers]
        active = [c for c in columns if c in headers]

        rows = []
        for row in reader:
            for col in active:
                val = row[col]
                row[col] = "***" if mask else (_hash(val) if val else "")
            rows.append(row)
            result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return result
