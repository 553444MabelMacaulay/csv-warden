"""Truncate string values in a column to a maximum character length."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TruncateResult:
    input_path: str
    output_path: str
    column: str
    max_length: int
    rows_total: int = 0
    rows_truncated: int = 0
    errors: list[str] = field(default_factory=list)


def summary(result: TruncateResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"Column : {result.column}",
        f"Max len: {result.max_length}",
        f"Rows   : {result.rows_total}",
        f"Truncated: {result.rows_truncated}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def truncate_csv(
    input_path: str,
    output_path: str,
    column: str,
    max_length: int,
    suffix: Optional[str] = "",
) -> TruncateResult:
    result = TruncateResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        max_length=max_length,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if max_length < 0:
        result.errors.append("max_length must be >= 0")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("File is empty or has no header")
            return result

        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found")
            return result

        rows: list[dict] = []
        for row in reader:
            result.rows_total += 1
            val = row[column]
            if len(val) > max_length:
                row[column] = val[:max_length] + (suffix or "")
                result.rows_truncated += 1
            rows.append(row)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
