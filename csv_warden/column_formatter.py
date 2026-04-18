"""Format column values using common string formatting patterns."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

SUPPORTED_FORMATS = ("title", "upper", "lower", "strip", "capitalize")


@dataclass
class FormatResult:
    input_file: str
    output_file: str
    columns_formatted: List[str] = field(default_factory=list)
    rows_affected: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: FormatResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file}",
        f"Columns formatted: {', '.join(result.columns_formatted) or 'none'}",
        f"Rows affected    : {result.rows_affected}",
    ]
    if result.errors:
        lines.append("Errors:")
        lines.extend(f"  - {e}" for e in result.errors)
    return "\n".join(lines)


def _fmt(value: str, fmt: str) -> str:
    if fmt == "title":
        return value.title()
    if fmt == "upper":
        return value.upper()
    if fmt == "lower":
        return value.lower()
    if fmt == "strip":
        return value.strip()
    if fmt == "capitalize":
        return value.capitalize()
    return value


def format_csv(
    input_path: str,
    output_path: str,
    column_formats: Dict[str, str],
) -> FormatResult:
    src = Path(input_path)
    result = FormatResult(input_file=input_path, output_file=output_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    for col, fmt in column_formats.items():
        if fmt not in SUPPORTED_FORMATS:
            result.errors.append(f"Unsupported format '{fmt}' for column '{col}'")
    if result.errors:
        return result

    rows: List[Dict[str, str]] = []
    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        headers = list(reader.fieldnames)
        for row in reader:
            rows.append(dict(row))

    missing = [c for c in column_formats if c not in headers]
    if missing:
        result.errors.append(f"Columns not found: {', '.join(missing)}")
        return result

    result.columns_formatted = list(column_formats.keys())
    out_rows = []
    for row in rows:
        new_row = dict(row)
        changed = False
        for col, fmt in column_formats.items():
            original = new_row[col]
            new_row[col] = _fmt(original, fmt)
            if new_row[col] != original:
                changed = True
        if changed:
            result.rows_affected += 1
        out_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
