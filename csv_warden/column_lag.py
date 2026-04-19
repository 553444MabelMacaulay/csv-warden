"""Shift a numeric column by N rows (lag/lead)."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LagResult:
    input_file: str
    column: str
    n: int
    rows_written: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: LagResult) -> str:
    lines = [
        f"Input   : {r.input_file}",
        f"Column  : {r.column}",
        f"Lag (n) : {r.n}",
        f"Rows    : {r.rows_written}",
    ]
    if r.errors:
        lines.append("Errors  :")
        for e in r.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def lag_csv(
    input_file: str,
    output_file: str,
    column: str,
    n: int = 1,
    fill_value: str = "",
    new_column: Optional[str] = None,
) -> LagResult:
    result = LagResult(input_file=input_file, column=column, n=n)
    src = Path(input_file)
    if not src.exists():
        result.errors.append(f"File not found: {input_file}")
        return result

    with open(input_file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable file.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    dest_col = new_column if new_column else f"{column}_lag{n}"
    if dest_col not in fieldnames:
        fieldnames = fieldnames + [dest_col]

    values = [row[column] for row in rows]
    if n >= 0:
        lagged = [fill_value] * min(n, len(values)) + values[: max(0, len(values) - n)]
    else:
        lead = abs(n)
        lagged = values[lead:] + [fill_value] * min(lead, len(values))

    for row, val in zip(rows, lagged):
        row[dest_col] = val

    with open(output_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    result.rows_written = len(rows)
    return result
