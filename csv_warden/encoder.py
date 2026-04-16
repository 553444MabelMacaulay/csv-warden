"""Re-encode CSV files to a target character encoding."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EncodeResult:
    input_file: str
    output_file: str
    source_encoding: str
    target_encoding: str
    rows_written: int = 0
    errors: list[str] = field(default_factory=list)
    success: bool = True


def summary(result: EncodeResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file}",
        f"Source encoding : {result.source_encoding}",
        f"Target encoding : {result.target_encoding}",
        f"Rows written    : {result.rows_written}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    else:
        lines.append("Status: OK")
    return "\n".join(lines)


def encode_csv(
    input_path: str,
    output_path: str,
    source_encoding: str = "utf-8",
    target_encoding: str = "utf-8",
    errors: str = "replace",
) -> EncodeResult:
    src = Path(input_path)
    result = EncodeResult(
        input_file=input_path,
        output_file=output_path,
        source_encoding=source_encoding,
        target_encoding=target_encoding,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        result.success = False
        return result

    try:
        with src.open(encoding=source_encoding, errors=errors, newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.errors.append("Empty or header-less file.")
                result.success = False
                return result
            fieldnames = list(reader.fieldnames)
            rows = list(reader)

        with open(output_path, "w", encoding=target_encoding, newline="") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            result.rows_written = len(rows)

    except (LookupError, UnicodeError) as exc:
        result.errors.append(str(exc))
        result.success = False

    return result
