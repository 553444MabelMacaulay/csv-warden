"""Convert CSV files to other formats (JSON, TSV, etc.)."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

SUPPORTED_FORMATS = ("json", "tsv")


@dataclass
class ConvertResult:
    input_file: str
    output_file: str
    output_format: str
    rows_written: int = 0
    errors: List[str] = field(default_factory=list)
    success: bool = True


def summary(result: ConvertResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file} ({result.output_format.upper()})",
        f"Rows written: {result.rows_written}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def convert_csv(
    input_path: str,
    output_path: str,
    output_format: str = "json",
) -> ConvertResult:
    fmt = output_format.lower().strip()
    result = ConvertResult(
        input_file=input_path,
        output_file=output_path,
        output_format=fmt,
    )

    if fmt not in SUPPORTED_FORMATS:
        result.errors.append(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
        result.success = False
        return result

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        result.success = False
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        result.errors.append("Input file is empty or has no data rows.")
        result.success = False
        return result

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        with out.open("w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2)
    elif fmt == "tsv":
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=rows[0].keys(), delimiter="\t"
            )
            writer.writeheader()
            writer.writerows(rows)

    result.rows_written = len(rows)
    return result
