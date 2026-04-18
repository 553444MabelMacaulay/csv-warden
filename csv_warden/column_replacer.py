"""column_replacer.py – replace values in a column using regex or exact match."""
from __future__ import annotations
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ReplaceResult:
    input_path: str
    output_path: str
    column: str
    replacements_made: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: ReplaceResult) -> str:
    lines = [
        f"Input : {r.input_path}",
        f"Output: {r.output_path}",
        f"Column: {r.column}",
        f"Replacements made: {r.replacements_made}",
    ]
    if r.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in r.errors)
    return "\n".join(lines)


def replace_csv(
    input_path: str,
    output_path: str,
    column: str,
    pattern: str,
    replacement: str,
    use_regex: bool = False,
    ignore_case: bool = False,
) -> ReplaceResult:
    result = ReplaceResult(input_path=input_path, output_path=output_path, column=column)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern if use_regex else re.escape(pattern), flags)

    rows: list[dict] = []
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in reader.fieldnames:
            result.errors.append(f"Column '{column}' not found in CSV.")
            return result
        fieldnames = list(reader.fieldnames)
        for row in reader:
            original = row[column]
            new_val = compiled.sub(replacement, original)
            if new_val != original:
                result.replacements_made += 1
            row[column] = new_val
            rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
