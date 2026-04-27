"""Extract named capture groups from a column into new columns via regex."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RegexExtractResult:
    input_path: str
    output_path: str
    column: str
    pattern: str
    rows_total: int = 0
    rows_matched: int = 0
    new_columns: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: RegexExtractResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Column: {result.column}",
        f"Pattern: {result.pattern}",
        f"Rows total  : {result.rows_total}",
        f"Rows matched: {result.rows_matched}",
        f"New columns : {', '.join(result.new_columns) if result.new_columns else '(none)'}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def regex_extract_csv(
    input_path: str,
    output_path: str,
    column: str,
    pattern: str,
    drop_original: bool = False,
    fill_value: str = "",
) -> RegexExtractResult:
    result = RegexExtractResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        pattern=pattern,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        result.errors.append(f"Invalid regex pattern: {exc}")
        return result

    group_names: List[str] = list(compiled.groupindex.keys())
    if not group_names:
        result.errors.append("Pattern has no named capture groups (use (?P<name>...))")
        return result

    result.new_columns = group_names

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no headers")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found in headers")
            return result

        out_fields = [f for f in fieldnames if not (drop_original and f == column)]
        for g in group_names:
            if g not in out_fields:
                out_fields.append(g)

        rows: List[Dict[str, str]] = []
        for row in reader:
            result.rows_total += 1
            m = compiled.search(row.get(column, "") or "")
            if m:
                result.rows_matched += 1
                captures = m.groupdict(default=fill_value)
            else:
                captures = {g: fill_value for g in group_names}
            out_row = {k: v for k, v in row.items() if k in out_fields}
            out_row.update(captures)
            rows.append(out_row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    return result
