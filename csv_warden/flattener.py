"""Flatten nested JSON-like string columns in a CSV."""
from __future__ import annotations
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class FlattenResult:
    input_file: str
    output_file: str
    rows_processed: int = 0
    columns_expanded: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: FlattenResult) -> str:
    lines = [
        f"Input:            {result.input_file}",
        f"Output:           {result.output_file}",
        f"Rows processed:   {result.rows_processed}",
        f"Columns expanded: {', '.join(result.columns_expanded) or 'none'}",
    ]
    if result.errors:
        lines.append(f"Errors:           {len(result.errors)}")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def flatten_csv(
    input_path: str,
    output_path: str,
    columns: Optional[List[str]] = None,
) -> FlattenResult:
    src = Path(input_path)
    result = FlattenResult(input_file=input_path, output_file=output_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header.
        target_cols = columns if columns else list(reader.fieldnames)
        rows = list(reader)

    if not rows:
        result.errors.append("No data rows found.")
        return result

    expanded: dict[str, set] = {}
    for row in rows:
        for col in target_cols:
            if col not in row:
                continue
            try:
                parsed = json.loads(row[col])
                if isinstance(parsed, dict):
                    for k in parsed:
                        expanded.setdefault(col, set()).add(k)
            except (json.JSONDecodeError, TypeError):
                pass

    base_fields = [f for f in reader.fieldnames if f not in expanded]
    new_fields = list(base_fields)
    for col, keys in expanded.items():
        for k in sorted(keys):
            new_fields.append(f"{col}.{k}")
        result.columns_expanded.append(col)

    out_rows = []
    for row in rows:
        new_row = {f: row.get(f, "") for f in base_fields}
        for col, keys in expanded.items():
            try:
                parsed = json.loads(row.get(col, "{}"))
            except (json.JSONDecodeError, TypeError):
                parsed = {}
            for k in sorted(keys):
                new_row[f"{col}.{k}"] = parsed.get(k, "")
        out_rows.append(new_row)
        result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
