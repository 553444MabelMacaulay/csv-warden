"""Winsorize numeric columns by capping values at given percentile bounds."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class WinsorizeResult:
    input_path: str
    output_path: str
    columns: list[str] = field(default_factory=list)
    rows_affected: int = 0
    errors: list[str] = field(default_factory=list)


def summary(result: WinsorizeResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Columns winsorized: {', '.join(result.columns) or 'none'}",
        f"Rows affected     : {result.rows_affected}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (len(sorted_vals) - 1) * pct / 100.0
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


def winsorize_csv(
    input_path: str,
    output_path: str,
    columns: list[str],
    lower_pct: float = 5.0,
    upper_pct: float = 95.0,
) -> WinsorizeResult:
    src = Path(input_path)
    result = WinsorizeResult(input_path=input_path, output_path=output_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable CSV.")
            return result
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    bounds: dict[str, tuple[float, float]] = {}
    for col in columns:
        if col not in fieldnames:
            result.errors.append(f"Column not found: {col}")
            continue
        vals = []
        for row in rows:
            try:
                vals.append(float(row[col]))
            except (ValueError, TypeError):
                pass
        if not vals:
            result.errors.append(f"No numeric values in column: {col}")
            continue
        lo = _percentile(vals, lower_pct)
        hi = _percentile(vals, upper_pct)
        bounds[col] = (lo, hi)
        result.columns.append(col)

    out_rows = []
    for row in rows:
        new_row = dict(row)
        changed = False
        for col, (lo, hi) in bounds.items():
            try:
                v = float(new_row[col])
                clamped = max(lo, min(hi, v))
                if clamped != v:
                    changed = True
                new_row[col] = str(clamped)
            except (ValueError, TypeError):
                pass
        if changed:
            result.rows_affected += 1
        out_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
