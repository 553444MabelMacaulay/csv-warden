"""Merge multiple columns into a single new column."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class MergeColResult:
    input_file: str
    output_file: str
    columns: List[str]
    new_column: str
    separator: str
    rows_processed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: MergeColResult) -> str:
    lines = [
        f"Input:       {result.input_file}",
        f"Output:      {result.output_file}",
        f"Merged:      {result.columns} -> '{result.new_column}' (sep={repr(result.separator)})",
        f"Rows:        {result.rows_processed}",
    ]
    if result.errors:
        lines.append(f"Errors:      {len(result.errors)}")
        for e in result.errors:
            lines.append(f"  - {e}")
    else:
        lines.append("Status:      OK")
    return "\n".join(lines)


def merge_columns(
    input_path: str,
    output_path: str,
    columns: List[str],
    new_column: str,
    separator: str = " ",
    drop_originals: bool = False,
) -> MergeColResult:
    inp = Path(input_path)
    result = MergeColResult(
        input_file=input_path,
        output_file=output_path,
        columns=columns,
        new_column=new_column,
        separator=separator,
    )

    if not inp.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(inp, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header.")
            return result

        missing = [c for c in columns if c not in reader.fieldnames]
        if missing:
            result.errors.append(f"Columns not found: {missing}")
            return result

        out_fields = list(reader.fieldnames)
        if new_column not in out_fields:
            out_fields.append(new_column)
        if drop_originals:
            out_fields = [f for f in out_fields if f not in columns] + ([new_column] if new_column not in [f for f in out_fields if f not in columns] else [])
            # ensure new_column present
            if new_column not in out_fields:
                out_fields.append(new_column)

        rows = list(reader)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            row[new_column] = separator.join(row.get(c, "") for c in columns)
            if drop_originals:
                for c in columns:
                    if c != new_column:
                        row.pop(c, None)
            writer.writerow({k: row[k] for k in out_fields})
            result.rows_processed += 1

    return result
