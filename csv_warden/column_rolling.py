from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class RollingResult:
    input_path: str
    output_path: str
    column: str
    window: int
    func: str
    new_column: str
    rows_processed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: RollingResult) -> str:
    lines = [
        f"Input:        {r.input_path}",
        f"Output:       {r.output_path}",
        f"Column:       {r.column}",
        f"Window:       {r.window}",
        f"Function:     {r.func}",
        f"New column:   {r.new_column}",
        f"Rows:         {r.rows_processed}",
    ]
    if r.errors:
        lines.append(f"Errors:       {len(r.errors)}")
        for e in r.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def _apply(func: str, values: List[float]) -> Optional[float]:
    if not values:
        return None
    if func == "mean":
        return sum(values) / len(values)
    if func == "sum":
        return sum(values)
    if func == "min":
        return min(values)
    if func == "max":
        return max(values)
    return None


def rolling_csv(
    input_path: str,
    output_path: str,
    column: str,
    window: int,
    func: str = "mean",
    new_column: Optional[str] = None,
) -> RollingResult:
    src = Path(input_path)
    if not src.exists():
        r = RollingResult(input_path, output_path, column, window, func, new_column or f"{column}_rolling_{func}")
        r.errors.append(f"File not found: {input_path}")
        return r

    if func not in ("mean", "sum", "min", "max"):
        r = RollingResult(input_path, output_path, column, window, func, new_column or f"{column}_rolling_{func}")
        r.errors.append(f"Unsupported function: {func}")
        return r

    out_col = new_column or f"{column}_rolling_{func}"
    result = RollingResult(input_path, output_path, column, window, func, out_col)

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in reader.fieldnames:
            result.errors.append(f"Column not found: {column}")
            return result
        rows = list(reader)
        fieldnames = list(reader.fieldnames) + [out_col]

    numeric: List[Optional[float]] = []
    for row in rows:
        try:
            numeric.append(float(row[column]))
        except (ValueError, TypeError):
            numeric.append(None)

    out_rows = []
    for i, row in enumerate(rows):
        window_vals = [v for v in numeric[max(0, i - window + 1): i + 1] if v is not None]
        val = _apply(func, window_vals)
        row[out_col] = "" if val is None else str(round(val, 10)).rstrip("0").rstrip(".")
        out_rows.append(row)
        result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
