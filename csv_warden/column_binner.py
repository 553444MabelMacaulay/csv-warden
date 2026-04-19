from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class BinResult:
    input_file: str
    output_file: str
    column: str
    bins: int
    rows_processed: int = 0
    rows_binned: int = 0
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Input:        {self.input_file}",
            f"Output:       {self.output_file}",
            f"Column:       {self.column}",
            f"Bins:         {self.bins}",
            f"Rows:         {self.rows_processed}",
            f"Rows binned:  {self.rows_binned}",
        ]
        if self.errors:
            lines.append(f"Errors:       {len(self.errors)}")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


def bin_csv(
    input_file: str,
    output_file: str,
    column: str,
    bins: int = 5,
    labels: Optional[List[str]] = None,
    new_column: Optional[str] = None,
) -> BinResult:
    result = BinResult(
        input_file=input_file,
        output_file=output_file,
        column=column,
        bins=bins,
    )
    p = Path(input_file)
    if not p.exists():
        result.errors.append(f"File not found: {input_file}")
        return result

    with open(input_file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable CSV.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        rows = list(reader)

    result.rows_processed = len(rows)
    out_col = new_column or f"{column}_bin"

    values: List[Optional[float]] = []
    for row in rows:
        try:
            values.append(float(row[column]))
        except (ValueError, TypeError):
            values.append(None)

    valid = [v for v in values if v is not None]
    if not valid:
        result.errors.append(f"No numeric values found in column '{column}'.")
        return result

    mn, mx = min(valid), max(valid)
    step = (mx - mn) / bins if mx != mn else 1.0

    def _label(v: float) -> str:
        idx = min(int((v - mn) / step), bins - 1)
        if labels and idx < len(labels):
            return labels[idx]
        lo = mn + idx * step
        hi = lo + step
        return f"[{lo:.4g}, {hi:.4g})"

    out_fields = fieldnames + [out_col]
    with open(output_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        for row, v in zip(rows, values):
            if v is not None:
                row[out_col] = _label(v)
                result.rows_binned += 1
            else:
                row[out_col] = ""
            writer.writerow(row)

    return result
