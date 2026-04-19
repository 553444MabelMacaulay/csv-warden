"""Scale numeric column values using min-max or z-score normalization."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ScaleResult:
    input_path: str
    output_path: str
    column: str
    method: str
    rows_scaled: int = 0
    rows_skipped: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: ScaleResult) -> str:
    lines = [
        f"Input:        {r.input_path}",
        f"Output:       {r.output_path}",
        f"Column:       {r.column}",
        f"Method:       {r.method}",
        f"Rows scaled:  {r.rows_scaled}",
        f"Rows skipped: {r.rows_skipped}",
    ]
    if r.errors:
        lines.append("Errors:")
        for e in r.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def scale_csv(
    input_path: str,
    output_path: str,
    column: str,
    method: str = "minmax",
) -> ScaleResult:
    result = ScaleResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        method=method,
    )

    if method not in ("minmax", "zscore"):
        result.errors.append(f"Unknown method '{method}'. Use 'minmax' or 'zscore'.")
        return result

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if column not in fieldnames:
        result.errors.append(f"Column '{column}' not found.")
        return result

    numeric: List[Optional[float]] = []
    for row in rows:
        try:
            numeric.append(float(row[column]))
        except (ValueError, TypeError):
            numeric.append(None)

    valid = [v for v in numeric if v is not None]
    if not valid:
        result.errors.append("No numeric values found in column.")
        return result

    if method == "minmax":
        lo, hi = min(valid), max(valid)
        spread = hi - lo if hi != lo else 1.0
        scale = lambda v: (v - lo) / spread
    else:  # zscore
        mean = sum(valid) / len(valid)
        variance = sum((v - mean) ** 2 for v in valid) / len(valid)
        std = variance ** 0.5 if variance > 0 else 1.0
        scale = lambda v: (v - mean) / std

    out_rows = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        if numeric[i] is not None:
            new_row[column] = f"{scale(numeric[i]):.6f}"
            result.rows_scaled += 1
        else:
            result.rows_skipped += 1
        out_rows.append(new_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
