"""column_interpolator.py – fill numeric gaps using linear or forward interpolation."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class InterpolateResult:
    input_path: str
    output_path: str
    column: str
    method: str
    rows_filled: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: InterpolateResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"Column : {result.column}  method={result.method}",
        f"Filled : {result.rows_filled} gap(s)",
    ]
    if result.errors:
        lines.append("Errors :")
        lines.extend(f"  {e}" for e in result.errors)
    return "\n".join(lines)


def _is_missing(value: str) -> bool:
    return value.strip() == ""


def _linear_interpolate(values: List[Optional[float]]) -> List[Optional[float]]:
    """Fill interior None gaps using linear interpolation."""
    result = list(values)
    n = len(result)
    i = 0
    while i < n:
        if result[i] is None:
            left_idx = i - 1
            right_idx = i
            while right_idx < n and result[right_idx] is None:
                right_idx += 1
            if left_idx >= 0 and right_idx < n:
                left_val = result[left_idx]
                right_val = result[right_idx]
                span = right_idx - left_idx
                for k in range(left_idx + 1, right_idx):
                    t = (k - left_idx) / span
                    result[k] = left_val + t * (right_val - left_val)
            i = right_idx
        else:
            i += 1
    return result


def _forward_fill(values: List[Optional[float]]) -> List[Optional[float]]:
    result = list(values)
    last = None
    for i, v in enumerate(result):
        if v is not None:
            last = v
        elif last is not None:
            result[i] = last
    return result


def interpolate_csv(
    input_path: str,
    output_path: str,
    column: str,
    method: str = "linear",
) -> InterpolateResult:
    src = Path(input_path)
    result = InterpolateResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        method=method,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if method not in ("linear", "forward"):
        result.errors.append(f"Unknown method '{method}'; use 'linear' or 'forward'.")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    raw: List[Optional[float]] = []
    for row in rows:
        val = row[column]
        if _is_missing(val):
            raw.append(None)
        else:
            try:
                raw.append(float(val))
            except ValueError:
                raw.append(None)

    filled = _linear_interpolate(raw) if method == "linear" else _forward_fill(raw)

    for i, (orig, new_val) in enumerate(zip(raw, filled)):
        if orig is None and new_val is not None:
            rows[i][column] = str(new_val)
            result.rows_filled += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
