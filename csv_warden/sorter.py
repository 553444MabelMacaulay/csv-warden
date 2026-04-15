"""Sort CSV rows by one or more columns."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SortResult:
    input_file: str
    output_file: str
    rows_sorted: int
    sort_columns: List[str]
    ascending: bool
    errors: List[str] = field(default_factory=list)


def summary(result: SortResult) -> str:
    lines = [
        f"Input  : {result.input_file}",
        f"Output : {result.output_file}",
        f"Columns: {', '.join(result.sort_columns)}",
        f"Order  : {'ascending' if result.ascending else 'descending'}",
        f"Rows   : {result.rows_sorted}",
    ]
    if result.errors:
        lines.append("Errors :")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def sort_csv(
    input_path: str,
    output_path: str,
    sort_columns: List[str],
    ascending: bool = True,
    missing_value: str = "",
) -> SortResult:
    """Sort *input_path* by *sort_columns* and write to *output_path*."""
    result = SortResult(
        input_file=input_path,
        output_file=output_path,
        rows_sorted=0,
        sort_columns=sort_columns,
        ascending=ascending,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("File is empty or has no header.")
            return result

        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    missing_cols = [c for c in sort_columns if c not in fieldnames]
    if missing_cols:
        result.errors.append(
            f"Sort column(s) not found in header: {', '.join(missing_cols)}"
        )
        return result

    def sort_key(row: dict):
        return tuple(row.get(col, missing_value) for col in sort_columns)

    sorted_rows = sorted(rows, key=sort_key, reverse=not ascending)

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)

    result.rows_sorted = len(sorted_rows)
    return result
