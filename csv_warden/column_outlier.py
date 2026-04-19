from __future__ import annotations
import csv
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class OutlierResult:
    input_file: str
    column: str
    method: str
    rows_flagged: int = 0
    rows_total: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: OutlierResult) -> str:
    lines = [
        f"Outlier Detection — {r.input_file}",
        f"  Column  : {r.column}",
        f"  Method  : {r.method}",
        f"  Rows    : {r.rows_total}",
        f"  Flagged : {r.rows_flagged}",
    ]
    if r.errors:
        lines.append("  Errors:")
        for e in r.errors:
            lines.append(f"    - {e}")
    return "\n".join(lines)


def _parse_floats(rows: list[dict], column: str) -> tuple[list[float], list[int]]:
    values, indices = [], []
    for i, row in enumerate(rows):
        try:
            values.append(float(row[column]))
            indices.append(i)
        except (ValueError, TypeError):
            pass
    return values, indices


def detect_outliers(
    input_path: str,
    output_path: str,
    column: str,
    method: str = "zscore",
    threshold: float = 3.0,
    flag_column: str = "_outlier",
) -> OutlierResult:
    p = Path(input_path)
    result = OutlierResult(input_file=input_path, column=column, method=method)

    if not p.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(p, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if column not in fieldnames:
        result.errors.append(f"Column '{column}' not found")
        return result

    result.rows_total = len(rows)
    values, valid_idx = _parse_floats(rows, column)

    if len(values) < 2:
        result.errors.append("Not enough numeric values to detect outliers")
        return result

    flagged: set[int] = set()

    if method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            pass
        else:
            for idx, val in zip(valid_idx, values):
                if abs((val - mean) / stdev) > threshold:
                    flagged.add(idx)
    elif method == "iqr":
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[(3 * n) // 4]
        iqr = q3 - q1
        lo, hi = q1 - threshold * iqr, q3 + threshold * iqr
        for idx, val in zip(valid_idx, values):
            if val < lo or val > hi:
                flagged.add(idx)
    else:
        result.errors.append(f"Unknown method: {method}")
        return result

    result.rows_flagged = len(flagged)
    out_fields = fieldnames + [flag_column]

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        for i, row in enumerate(rows):
            row[flag_column] = "1" if i in flagged else "0"
            writer.writerow(row)

    return result
