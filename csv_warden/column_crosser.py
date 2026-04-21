"""Cross-tabulation (contingency table) for two categorical columns."""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CrossResult:
    input_file: str
    row_col: str
    col_col: str
    output_file: str
    row_labels: List[str] = field(default_factory=list)
    col_labels: List[str] = field(default_factory=list)
    table: Dict[str, Dict[str, int]] = field(default_factory=dict)
    error: Optional[str] = None


def summary(result: CrossResult) -> str:
    if result.error:
        return f"[ERROR] {result.error}"
    rows = len(result.row_labels)
    cols = len(result.col_labels)
    return (
        f"Cross-tabulation: '{result.row_col}' x '{result.col_col}'\n"
        f"  Unique row values : {rows}\n"
        f"  Unique col values : {cols}\n"
        f"  Output            : {result.output_file}"
    )


def cross_csv(
    input_file: str,
    row_col: str,
    col_col: str,
    output_file: str,
) -> CrossResult:
    result = CrossResult(
        input_file=input_file,
        row_col=row_col,
        col_col=col_col,
        output_file=output_file,
    )

    path = Path(input_file)
    if not path.exists():
        result.error = f"File not found: {input_file}"
        return result

    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    col_values: set = set()

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.error = "Empty or missing header"
            return result
        if row_col not in reader.fieldnames:
            result.error = f"Column '{row_col}' not found"
            return result
        if col_col not in reader.fieldnames:
            result.error = f"Column '{col_col}' not found"
            return result

        for row in reader:
            rv = row[row_col]
            cv = row[col_col]
            counts[rv][cv] += 1
            col_values.add(cv)

    result.row_labels = sorted(counts.keys())
    result.col_labels = sorted(col_values)
    result.table = {r: dict(counts[r]) for r in result.row_labels}

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([f"{row_col}\\{col_col}"] + result.col_labels)
        for rv in result.row_labels:
            writer.writerow(
                [rv] + [result.table[rv].get(cv, 0) for cv in result.col_labels]
            )

    return result
