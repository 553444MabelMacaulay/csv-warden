"""Parse and reformat date columns in a CSV file."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import List, Optional


@dataclass
class DateParseResult:
    input_file: str
    output_file: str
    column: str
    input_fmt: str
    output_fmt: str
    rows_converted: int = 0
    rows_failed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: DateParseResult) -> str:
    lines = [
        f"Input : {r.input_file}",
        f"Output: {r.output_file}",
        f"Column: {r.column}",
        f"Format: {r.input_fmt} -> {r.output_fmt}",
        f"Converted : {r.rows_converted}",
        f"Failed    : {r.rows_failed}",
    ]
    if r.errors:
        lines.append("Errors:")
        for e in r.errors[:5]:
            lines.append(f"  {e}")
    return "\n".join(lines)


def parse_dates(
    input_path: str,
    output_path: str,
    column: str,
    input_fmt: str,
    output_fmt: str,
    errors: str = "coerce",
) -> DateParseResult:
    src = Path(input_path)
    result = DateParseResult(
        input_file=input_path,
        output_file=output_path,
        column=column,
        input_fmt=input_fmt,
        output_fmt=output_fmt,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    out_rows = []
    for i, row in enumerate(rows, start=2):
        raw = row[column]
        try:
            dt = datetime.strptime(raw, input_fmt)
            row[column] = dt.strftime(output_fmt)
            result.rows_converted += 1
        except (ValueError, TypeError) as exc:
            if errors == "coerce":
                result.rows_failed += 1
                result.errors.append(f"Row {i}: '{raw}' -> {exc}")
            else:
                raise
        out_rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
