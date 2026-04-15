"""Aggregation module for csv-warden.

Supports basic column aggregations: sum, mean, min, max, count.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


SUPPORTED_FUNCS = ("sum", "mean", "min", "max", "count")


@dataclass
class AggregateResult:
    input_file: str
    column: str
    func: str
    value: Optional[float] = None
    row_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def summary(result: AggregateResult) -> str:
    lines = [
        f"File      : {result.input_file}",
        f"Column    : {result.column}",
        f"Function  : {result.func}",
        f"Row count : {result.row_count}",
        f"Result    : {result.value}",
    ]
    if result.warnings:
        lines.append("Warnings  : " + "; ".join(result.warnings))
    if result.errors:
        lines.append("Errors    : " + "; ".join(result.errors))
    return "\n".join(lines)


def aggregate_csv(
    input_path: str,
    column: str,
    func: str,
) -> AggregateResult:
    result = AggregateResult(input_file=input_path, column=column, func=func)

    if func not in SUPPORTED_FUNCS:
        result.errors.append(
            f"Unsupported function '{func}'. Choose from: {', '.join(SUPPORTED_FUNCS)}"
        )
        return result

    path = Path(input_path)
    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    values: List[float] = []
    skipped = 0

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in (reader.fieldnames or []):
            result.errors.append(f"Column '{column}' not found in CSV.")
            return result

        for row in reader:
            result.row_count += 1
            raw = row[column].strip()
            if raw == "":
                skipped += 1
                continue
            try:
                values.append(float(raw))
            except ValueError:
                skipped += 1

    if skipped:
        result.warnings.append(
            f"{skipped} row(s) skipped (non-numeric or empty values)."
        )

    if not values:
        result.warnings.append("No numeric values found; result is None.")
        return result

    if func == "sum":
        result.value = sum(values)
    elif func == "mean":
        result.value = sum(values) / len(values)
    elif func == "min":
        result.value = min(values)
    elif func == "max":
        result.value = max(values)
    elif func == "count":
        result.value = float(len(values))

    return result
