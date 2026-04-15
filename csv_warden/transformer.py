"""Column transformation utilities for CSV files."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    input_path: str
    output_path: str
    rows_processed: int = 0
    columns_transformed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: TransformResult) -> str:
    lines = [
        f"Input:              {result.input_path}",
        f"Output:             {result.output_path}",
        f"Rows processed:     {result.rows_processed}",
        f"Columns transformed:{', '.join(result.columns_transformed) or 'none'}",
        f"Errors:             {len(result.errors)}",
    ]
    if result.errors:
        lines.append("Error details:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "title": str.title,
}


def transform_csv(
    input_path: str,
    output_path: str,
    column_transforms: Dict[str, str],
) -> TransformResult:
    """Apply named transforms to specified columns and write result.

    Args:
        input_path: Path to the source CSV.
        output_path: Path where transformed CSV will be written.
        column_transforms: Mapping of column name -> transform name
                           (e.g. {"name": "upper", "email": "lower"}).

    Returns:
        A TransformResult describing what happened.
    """
    result = TransformResult(input_path=input_path, output_path=output_path)
    src = Path(input_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    unknown = {k: v for k, v in column_transforms.items()
               if v not in BUILTIN_TRANSFORMS}
    for col, name in unknown.items():
        result.errors.append(
            f"Unknown transform '{name}' for column '{col}'; "
            f"valid options: {list(BUILTIN_TRANSFORMS)}"
        )
    if result.errors:
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no headers.")
            return result

        fieldnames = list(reader.fieldnames)
        missing = [c for c in column_transforms if c not in fieldnames]
        for col in missing:
            result.errors.append(
                f"Column '{col}' not found in CSV headers."
            )
        if result.errors:
            return result

        rows: List[Dict[str, str]] = []
        for row in reader:
            for col, tname in column_transforms.items():
                row[col] = BUILTIN_TRANSFORMS[tname](row[col])
            rows.append(row)
            result.rows_processed += 1

    result.columns_transformed = list(column_transforms.keys())

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
