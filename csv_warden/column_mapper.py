"""Map column values using a user-supplied mapping dictionary."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class MapResult:
    input_file: str
    output_file: str
    column: str
    mapped: int = 0
    unmapped: int = 0
    errors: list = field(default_factory=list)


def summary(r: MapResult) -> str:
    lines = [
        f"Input : {r.input_file}",
        f"Output: {r.output_file}",
        f"Column: {r.column}",
        f"Mapped  values : {r.mapped}",
        f"Unmapped values: {r.unmapped}",
    ]
    if r.errors:
        lines.append("Errors:")
        for e in r.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def map_csv(
    input_path: str,
    output_path: str,
    column: str,
    mapping: Dict[str, str],
    default: Optional[str] = None,
) -> MapResult:
    src = Path(input_path)
    result = MapResult(input_file=input_path, output_file=output_path, column=column)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    rows: list[dict] = []
    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in reader.fieldnames:
            result.errors.append(f"Column '{column}' not found in CSV.")
            return result
        fieldnames = list(reader.fieldnames)
        for row in reader:
            val = row[column]
            if val in mapping:
                row[column] = mapping[val]
                result.mapped += 1
            elif default is not None:
                row[column] = default
                result.unmapped += 1
            else:
                result.unmapped += 1
            rows.append(row)

    with Path(output_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
