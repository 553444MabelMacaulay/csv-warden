"""column_condenser.py — collapse multiple columns into one via a template."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CondenserResult:
    input_path: str
    output_path: str
    new_column: str
    template: str
    rows_processed: int = 0
    rows_failed: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: CondenserResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"New col: {result.new_column}",
        f"Template: {result.template}",
        f"Rows processed : {result.rows_processed}",
        f"Rows failed    : {result.rows_failed}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def condense_csv(
    input_path: str,
    output_path: str,
    template: str,
    new_column: str,
    drop_sources: bool = False,
) -> CondenserResult:
    """Render *template* for every row and write the result to *new_column*.

    Template placeholders are column names wrapped in braces, e.g.
    ``"{first} {last}"``.
    """
    src = Path(input_path)
    result = CondenserResult(
        input_path=input_path,
        output_path=output_path,
        new_column=new_column,
        template=template,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    placeholders = _PLACEHOLDER.findall(template)

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result

        missing = [p for p in placeholders if p not in reader.fieldnames]
        if missing:
            result.errors.append(f"Columns not found in CSV: {missing}")
            return result

        out_fields = list(reader.fieldnames)
        if new_column not in out_fields:
            out_fields.append(new_column)
        if drop_sources:
            out_fields = [c for c in out_fields if c not in placeholders or c == new_column]

        rows = []
        for row in reader:
            try:
                value = template.format(**{p: row.get(p, "") for p in placeholders})
                row[new_column] = value
                result.rows_processed += 1
            except (KeyError, ValueError) as exc:
                row[new_column] = ""
                result.rows_failed += 1
                result.errors.append(f"Row {result.rows_processed + result.rows_failed}: {exc}")
            rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return result
