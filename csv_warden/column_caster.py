"""Cast columns to specified data types."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

SUPPORTED_TYPES = {"int", "float", "str", "bool"}


@dataclass
class CastResult:
    input_file: str
    output_file: str
    casts_applied: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    rows_processed: int = 0
    success: bool = True


def summary(result: CastResult) -> str:
    lines = [
        f"Input:      {result.input_file}",
        f"Output:     {result.output_file}",
        f"Rows:       {result.rows_processed}",
        f"Casts:      {', '.join(f'{c}→{t}' for c, t in result.casts_applied.items()) or 'none'}",
    ]
    if result.errors:
        lines.append(f"Errors ({len(result.errors)}):")
        for e in result.errors[:5]:
            lines.append(f"  {e}")
    lines.append(f"Status:     {'OK' if result.success else 'FAILED'}")
    return "\n".join(lines)


def _cast_value(value: str, dtype: str) -> Optional[str]:
    if dtype == "int":
        return str(int(float(value)))
    if dtype == "float":
        return str(float(value))
    if dtype == "bool":
        return str(value.strip().lower() in {"1", "true", "yes"})
    return str(value)


def cast_csv(
    input_path: str,
    output_path: str,
    casts: Dict[str, str],
) -> CastResult:
    result = CastResult(input_file=input_path, output_file=output_path)

    unknown = {t for t in casts.values() if t not in SUPPORTED_TYPES}
    if unknown:
        result.errors.append(f"Unsupported types: {unknown}")
        result.success = False
        return result

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        result.success = False
        return result

    rows: List[Dict[str, str]] = []
    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        for i, row in enumerate(reader, start=2):
            new_row = dict(row)
            for col, dtype in casts.items():
                if col not in new_row:
                    continue
                try:
                    new_row[col] = _cast_value(new_row[col], dtype)
                    result.casts_applied[col] = dtype
                except (ValueError, TypeError) as exc:
                    result.errors.append(f"Row {i}, col '{col}': {exc}")
                    result.success = False
            rows.append(new_row)
            result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return result
