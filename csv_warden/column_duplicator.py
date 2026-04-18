"""Duplicate columns under new names."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DuplicateResult:
    input_path: str
    output_path: str
    duplicated: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: DuplicateResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Duplicated columns: {', '.join(result.duplicated) if result.duplicated else 'none'}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def duplicate_columns(
    input_path: str,
    output_path: str,
    mapping: Dict[str, str],
) -> DuplicateResult:
    """Copy columns src->dst as specified in mapping."""
    result = DuplicateResult(input_path=input_path, output_path=output_path)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        original_fields: List[str] = list(reader.fieldnames)
        rows = list(reader)

    new_fields = list(original_fields)
    for src_col, dst_col in mapping.items():
        if src_col not in original_fields:
            result.errors.append(f"Column not found: {src_col}")
            continue
        if dst_col in new_fields:
            result.errors.append(f"Target column already exists: {dst_col}")
            continue
        new_fields.append(dst_col)
        result.duplicated.append(f"{src_col}->{dst_col}")
        for row in rows:
            row[dst_col] = row[src_col]

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)

    return result
