from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class DropResult:
    input_file: str
    output_file: str
    columns_requested: List[str] = field(default_factory=list)
    columns_dropped: List[str] = field(default_factory=list)
    columns_not_found: List[str] = field(default_factory=list)
    rows_written: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: DropResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file}",
        f"Columns dropped   : {', '.join(result.columns_dropped) or 'none'}",
        f"Columns not found : {', '.join(result.columns_not_found) or 'none'}",
        f"Rows written      : {result.rows_written}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def drop_columns(
    input_path: str,
    output_path: str,
    columns: List[str],
) -> DropResult:
    result = DropResult(
        input_file=input_path,
        output_file=output_path,
        columns_requested=list(columns),
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.errors.append("CSV has no headers.")
                return result

            existing = set(reader.fieldnames)
            result.columns_dropped = [c for c in columns if c in existing]
            result.columns_not_found = [c for c in columns if c not in existing]
            keep = [f for f in reader.fieldnames if f not in set(columns)]

            rows = []
            for row in reader:
                rows.append({k: row[k] for k in keep})

        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keep)
            writer.writeheader()
            writer.writerows(rows)
            result.rows_written = len(rows)

    except Exception as exc:  # pragma: no cover
        result.errors.append(str(exc))

    return result
