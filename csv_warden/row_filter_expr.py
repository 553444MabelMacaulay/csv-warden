"""Filter rows using simple expression strings like 'age>30' or 'name==Alice'."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_PATTERN = re.compile(r"^(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)$")


@dataclass
class ExprFilterResult:
    input_rows: int = 0
    output_rows: int = 0
    skipped_rows: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: ExprFilterResult) -> str:
    return (
        f"Input rows: {r.input_rows}, Output rows: {r.output_rows}, "
        f"Skipped: {r.skipped_rows}, Errors: {len(r.errors)}"
    )


def _evaluate(row: dict, expr: str) -> Optional[bool]:
    m = _PATTERN.match(expr.strip())
    if not m:
        return None
    col, op, val = m.group(1), m.group(2), m.group(3).strip()
    cell = row.get(col)
    if cell is None:
        return False
    try:
        cell_f, val_f = float(cell), float(val)
        cell_cmp, val_cmp = cell_f, val_f
    except ValueError:
        cell_cmp, val_cmp = str(cell), str(val)
    ops = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
    }
    return ops[op](cell_cmp, val_cmp)


def filter_by_expr(
    input_path: str,
    output_path: str,
    expr: str,
    exclude: bool = False,
) -> ExprFilterResult:
    result = ExprFilterResult()
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    kept: List[dict] = []
    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        for row in reader:
            result.input_rows += 1
            match = _evaluate(row, expr)
            if match is None:
                result.errors.append(f"Invalid expression: {expr}")
                result.skipped_rows += 1
                continue
            keep = (not match) if exclude else match
            if keep:
                kept.append(row)
            else:
                result.skipped_rows += 1

    result.output_rows = len(kept)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept)
    return result
