"""Compute cumulative aggregations (sum, product, min, max) over a numeric column."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SUPPORTED_OPS = ("sum", "product", "min", "max")


@dataclass
class CumulateResult:
    input_path: str
    output_path: str
    column: str
    op: str
    new_column: str
    rows_processed: int = 0
    rows_skipped: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: CumulateResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"Column : {result.column}  op={result.op}  new_col={result.new_column}",
        f"Rows processed : {result.rows_processed}",
        f"Rows skipped   : {result.rows_skipped}",
    ]
    if result.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in result.errors)
    return "\n".join(lines)


def cumulate_csv(
    input_path: str,
    output_path: str,
    column: str,
    op: str = "sum",
    new_column: Optional[str] = None,
) -> CumulateResult:
    op = op.lower()
    if op not in SUPPORTED_OPS:
        raise ValueError(f"Unsupported op '{op}'. Choose from {SUPPORTED_OPS}.")

    if new_column is None:
        new_column = f"{column}_cum_{op}"

    src = Path(input_path)
    result = CumulateResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        op=op,
        new_column=new_column,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    rows = list(csv.DictReader(src.open(newline="", encoding="utf-8")))
    if not rows:
        result.errors.append("Input file is empty or has no data rows.")
        return result

    if column not in rows[0]:
        result.errors.append(f"Column '{column}' not found in headers.")
        return result

    running: Optional[float] = None
    out_rows = []
    for row in rows:
        raw = row[column].strip()
        try:
            val = float(raw)
            if running is None:
                running = val
            elif op == "sum":
                running += val
            elif op == "product":
                running *= val
            elif op == "min":
                running = min(running, val)
            elif op == "max":
                running = max(running, val)
            row[new_column] = str(running)
            result.rows_processed += 1
        except ValueError:
            row[new_column] = ""
            result.rows_skipped += 1
        out_rows.append(row)

    fieldnames = list(rows[0].keys())
    if new_column not in fieldnames:
        fieldnames.append(new_column)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    return result
