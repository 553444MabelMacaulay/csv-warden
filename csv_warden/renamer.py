"""Column renaming module for csv-warden."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    input_file: str
    output_file: Optional[str]
    rows_written: int
    renamed: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: RenameResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Output: {result.output_file or '(in-place preview)'}",
        f"Rows written : {result.rows_written}",
    ]
    if result.renamed:
        lines.append("Renamed columns:")
        for old, new in result.renamed.items():
            lines.append(f"  {old!r} -> {new!r}")
    if result.skipped:
        lines.append("Skipped (not found): " + ", ".join(result.skipped))
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def rename_csv(
    input_path: str,
    output_path: str,
    mapping: Dict[str, str],
) -> RenameResult:
    """Rename columns in *input_path* according to *mapping* and write to *output_path*.

    Keys in *mapping* that do not match any header are recorded in
    ``RenameResult.skipped`` but do not cause a failure.
    """
    src = Path(input_path)
    result = RenameResult(input_file=input_path, output_file=output_path, rows_written=0)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    try:
        with src.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.errors.append("File is empty or has no header row.")
                return result

            original_headers: List[str] = list(reader.fieldnames)
            new_headers: List[str] = []
            applied: Dict[str, str] = {}

            for col in original_headers:
                if col in mapping:
                    new_headers.append(mapping[col])
                    applied[col] = mapping[col]
                else:
                    new_headers.append(col)

            for requested in mapping:
                if requested not in original_headers:
                    result.skipped.append(requested)

            result.renamed = applied
            rows = list(reader)

        with Path(output_path).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=new_headers)
            writer.writeheader()
            for row in rows:
                new_row = {
                    (mapping.get(k, k)): v
                    for k, v in row.items()
                }
                writer.writerow(new_row)
                result.rows_written += 1

    except Exception as exc:  # pragma: no cover
        result.errors.append(str(exc))

    return result
