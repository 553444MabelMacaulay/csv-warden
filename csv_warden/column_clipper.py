"""Clip numeric column values to a specified [min, max] range."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ClipResult:
    input_path: str
    output_path: str
    column: str
    low: Optional[float]
    high: Optional[float]
    rows_clipped: int = 0
    rows_skipped: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: ClipResult) -> str:
    lines = [
        f"Input  : {r.input_path}",
        f"Output : {r.output_path}",
        f"Column : {r.column}  range=[{r.low}, {r.high}]",
        f"Clipped: {r.rows_clipped} value(s)",
        f"Skipped (non-numeric): {r.rows_skipped} value(s)",
    ]
    if r.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in r.errors)
    return "\n".join(lines)


def clip_csv(
    input_path: str,
    output_path: str,
    column: str,
    low: Optional[float] = None,
    high: Optional[float] = None,
) -> ClipResult:
    src = Path(input_path)
    result = ClipResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        low=low,
        high=high,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    out_rows = []
    for row in rows:
        raw = row[column].strip()
        try:
            val = float(raw)
            clipped = val
            if low is not None and val < low:
                clipped = low
            if high is not None and val > high:
                clipped = high
            if clipped != val:
                result.rows_clipped += 1
            # preserve int-like values
            row[column] = str(int(clipped)) if clipped == int(clipped) else str(clipped)
        except ValueError:
            result.rows_skipped += 1
        out_rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
