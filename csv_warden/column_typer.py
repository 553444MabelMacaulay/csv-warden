"""Infer and report likely data types for each column."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class ColumnType:
    name: str
    inferred_type: str  # int | float | bool | date | string
    sample_values: List[str] = field(default_factory=list)


@dataclass
class TypeResult:
    columns: List[ColumnType] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: TypeResult) -> str:
    lines = ["Column Type Inference"]
    lines.append(f"  Columns analysed : {len(result.columns)}")
    for ct in result.columns:
        lines.append(f"  {ct.name:<20} -> {ct.inferred_type}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def _infer(values: List[str]) -> str:
    non_empty = [v for v in values if v.strip() != ""]
    if not non_empty:
        return "string"
    for typ, cast in (("bool", lambda v: v.lower() in ("true", "false", "1", "0")),
                      ("int", lambda v: v.lstrip("-").isdigit()),
                      ("float", _try_float)):
        if all(cast(v) for v in non_empty):
            return typ
    import re
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if all(date_re.match(v) for v in non_empty):
        return "date"
    return "string"


def _try_float(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def infer_types(input_path: str, sample_size: int = 100) -> TypeResult:
    result = TypeResult()
    path = Path(input_path)
    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            result.errors.append("Empty or missing header row.")
            return result
        buckets: Dict[str, List[str]] = {col: [] for col in reader.fieldnames}
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            for col in reader.fieldnames:
                buckets[col].append(row.get(col, ""))
    for col, vals in buckets.items():
        result.columns.append(ColumnType(
            name=col,
            inferred_type=_infer(vals),
            sample_values=vals[:3],
        ))
    return result
