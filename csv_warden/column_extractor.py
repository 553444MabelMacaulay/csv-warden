"""Extract a substring from a column using start/end positions or a regex group."""
from __future__ import annotations
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ExtractResult:
    input_file: str
    column: str
    new_column: str
    rows_processed: int = 0
    rows_extracted: int = 0
    errors: list[str] = field(default_factory=list)


def summary(result: ExtractResult) -> str:
    lines = [
        f"Input:         {result.input_file}",
        f"Column:        {result.column} -> {result.new_column}",
        f"Rows processed:{result.rows_processed}",
        f"Rows extracted:{result.rows_extracted}",
    ]
    if result.errors:
        lines.append(f"Errors:        {len(result.errors)}")
        for e in result.errors[:5]:
            lines.append(f"  {e}")
    return "\n".join(lines)


def extract_csv(
    input_path: str,
    output_path: str,
    column: str,
    new_column: Optional[str] = None,
    pattern: Optional[str] = None,
    group: int = 0,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> ExtractResult:
    src = Path(input_path)
    if not src.exists():
        r = ExtractResult(input_file=input_path, column=column, new_column=new_column or column + "_extracted")
        r.errors.append(f"File not found: {input_path}")
        return r

    nc = new_column or column + "_extracted"
    result = ExtractResult(input_file=input_path, column=column, new_column=nc)
    compiled = re.compile(pattern) if pattern else None

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in reader.fieldnames:
            result.errors.append(f"Column '{column}' not found")
            return result
        fieldnames = list(reader.fieldnames) + [nc]
        rows = []
        for row in reader:
            result.rows_processed += 1
            val = row.get(column, "")
            extracted = ""
            if compiled:
                m = compiled.search(val)
                if m:
                    try:
                        extracted = m.group(group)
                        result.rows_extracted += 1
                    except IndexError:
                        result.errors.append(f"Row {result.rows_processed}: group {group} not found")
            elif start is not None or end is not None:
                extracted = val[start:end]
                if extracted:
                    result.rows_extracted += 1
            row[nc] = extracted
            rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
