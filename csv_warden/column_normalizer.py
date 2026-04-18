from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import re


@dataclass
class NormalizeResult:
    input_path: str
    output_path: str
    columns: List[str]
    rows_processed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: NormalizeResult) -> str:
    lines = [
        f"Input:      {result.input_path}",
        f"Output:     {result.output_path}",
        f"Columns:    {', '.join(result.columns)}",
        f"Rows:       {result.rows_processed}",
    ]
    if result.errors:
        lines.append(f"Errors:     {len(result.errors)}")
        for e in result.errors:
            lines.append(f"  - {e}")
    else:
        lines.append("Status:     OK")
    return "\n".join(lines)


def _normalize_value(value: str, mode: str) -> str:
    if mode == "snake_case":
        value = value.strip().lower()
        value = re.sub(r"[\s\-]+", "_", value)
        value = re.sub(r"[^a-z0-9_]", "", value)
        return value
    elif mode == "title_case":
        return value.strip().title()
    elif mode == "lower":
        return value.strip().lower()
    elif mode == "upper":
        return value.strip().upper()
    else:
        return value


def normalize_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
    mode: str = "snake_case",
) -> NormalizeResult:
    src = Path(input_path)
    result = NormalizeResult(input_path=input_path, output_path=output_path, columns=columns)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if mode not in ("snake_case", "title_case", "lower", "upper"):
        result.errors.append(f"Unsupported mode: {mode}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or invalid CSV file.")
            return result
        headers = list(reader.fieldnames)
        missing = [c for c in columns if c not in headers]
        if missing:
            result.errors.append(f"Columns not found: {', '.join(missing)}")
            return result
        rows = list(reader)

    out_rows = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            new_row[col] = _normalize_value(row[col], mode)
        out_rows.append(new_row)
        result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
