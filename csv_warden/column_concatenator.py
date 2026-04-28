"""Concatenate values from multiple columns into a new column."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ConcatResult:
    input_path: str
    output_path: str
    columns: List[str]
    new_column: str
    separator: str
    rows_written: int = 0
    missing_columns: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


def summary(result: ConcatResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"Columns: {', '.join(result.columns)}",
        f"New col: {result.new_column}  (sep={repr(result.separator)})",
        f"Rows   : {result.rows_written}",
    ]
    if result.missing_columns:
        lines.append(f"Missing: {', '.join(result.missing_columns)}")
    if not result.success:
        lines.append(f"Error  : {result.error}")
    return "\n".join(lines)


def concatenate_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
    new_column: str = "concatenated",
    separator: str = " ",
    drop_sources: bool = False,
) -> ConcatResult:
    src = Path(input_path)
    if not src.exists():
        return ConcatResult(
            input_path=input_path,
            output_path=output_path,
            columns=columns,
            new_column=new_column,
            separator=separator,
            success=False,
            error=f"File not found: {input_path}",
        )

    result = ConcatResult(
        input_path=input_path,
        output_path=output_path,
        columns=columns,
        new_column=new_column,
        separator=separator,
    )

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])

        missing = [c for c in columns if c not in fieldnames]
        if missing:
            result.missing_columns = missing
            result.success = False
            result.error = f"Columns not found: {', '.join(missing)}"
            return result

        out_fields = [f for f in fieldnames if not (drop_sources and f in columns)]
        if new_column not in out_fields:
            out_fields.append(new_column)

        rows = []
        for row in reader:
            parts = [row.get(c, "") for c in columns]
            row[new_column] = separator.join(parts)
            if drop_sources:
                for c in columns:
                    row.pop(c, None)
            rows.append(row)

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    result.rows_written = len(rows)
    return result
