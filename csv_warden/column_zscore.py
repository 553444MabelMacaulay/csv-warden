"""Compute z-score for a numeric column and write it to a new column."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ZScoreResult:
    input_path: str
    output_path: str
    column: str
    new_column: str
    rows_processed: int = 0
    rows_skipped: int = 0
    mean: Optional[float] = None
    std: Optional[float] = None
    errors: List[str] = field(default_factory=list)


def summary(result: ZScoreResult) -> str:
    lines = [
        f"Z-Score  : {result.column} -> {result.new_column}",
        f"Input    : {result.input_path}",
        f"Output   : {result.output_path}",
        f"Mean     : {result.mean:.4f}" if result.mean is not None else "Mean     : n/a",
        f"Std Dev  : {result.std:.4f}" if result.std is not None else "Std Dev  : n/a",
        f"Processed: {result.rows_processed}",
        f"Skipped  : {result.rows_skipped}",
    ]
    if result.errors:
        lines.append("Errors   : " + "; ".join(result.errors))
    return "\n".join(lines)


def zscore_csv(
    input_path: str,
    output_path: str,
    column: str,
    new_column: Optional[str] = None,
) -> ZScoreResult:
    src = Path(input_path)
    new_col = new_column or f"{column}_zscore"
    result = ZScoreResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        new_column=new_col,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable CSV.")
            return result
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if column not in fieldnames:
        result.errors.append(f"Column '{column}' not found.")
        return result

    # Parse numeric values
    values: List[Optional[float]] = []
    for row in rows:
        raw = row[column].strip()
        try:
            values.append(float(raw))
        except (ValueError, AttributeError):
            values.append(None)

    numeric = [v for v in values if v is not None]
    if not numeric:
        result.errors.append(f"No numeric values found in column '{column}'.")
        return result

    mean = sum(numeric) / len(numeric)
    variance = sum((v - mean) ** 2 for v in numeric) / len(numeric)
    std = math.sqrt(variance)
    result.mean = mean
    result.std = std

    out_fieldnames = fieldnames + [new_col]
    with Path(output_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fieldnames)
        writer.writeheader()
        for row, val in zip(rows, values):
            if val is not None and std > 0:
                row[new_col] = f"{(val - mean) / std:.6f}"
                result.rows_processed += 1
            elif val is not None and std == 0:
                row[new_col] = "0.000000"
                result.rows_processed += 1
            else:
                row[new_col] = ""
                result.rows_skipped += 1
            writer.writerow(row)

    return result
