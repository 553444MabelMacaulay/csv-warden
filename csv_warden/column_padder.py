"""Pad string values in CSV columns to a fixed width."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PadResult:
    input_file: str
    output_file: str
    columns_padded: List[str] = field(default_factory=list)
    rows_affected: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: PadResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file}",
        f"Columns padded : {', '.join(result.columns_padded) or 'none'}",
        f"Rows affected  : {result.rows_affected}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def pad_csv(
    input_path: str,
    output_path: str,
    widths: Dict[str, int],
    align: str = "left",
    fill_char: str = " ",
) -> PadResult:
    """Pad columns to fixed widths. align: 'left' or 'right'."""
    src = Path(input_path)
    result = PadResult(input_file=input_path, output_file=output_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if align not in ("left", "right"):
        result.errors.append(f"Invalid align value: {align!r}. Use 'left' or 'right'.")
        return result

    if len(fill_char) != 1:
        result.errors.append("fill_char must be a single character.")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no headers.")
            return result
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    unknown = [c for c in widths if c not in fieldnames]
    for col in unknown:
        result.errors.append(f"Column not found: {col!r}")

    valid_widths = {c: w for c, w in widths.items() if c in fieldnames}
    result.columns_padded = list(valid_widths.keys())

    out_rows = []
    for row in rows:
        new_row = dict(row)
        changed = False
        for col, width in valid_widths.items():
            val = new_row.get(col, "") or ""
            if align == "left":
                padded = val.ljust(width, fill_char)
            else:
                padded = val.rjust(width, fill_char)
            if padded != val:
                changed = True
            new_row[col] = padded
        if changed:
            result.rows_affected += 1
        out_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
