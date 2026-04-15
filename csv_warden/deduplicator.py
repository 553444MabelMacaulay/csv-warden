"""Deduplication module for csv-warden."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class DeduplicateResult:
    input_rows: int = 0
    output_rows: int = 0
    duplicates_removed: int = 0
    duplicate_lines: List[int] = field(default_factory=list)  # 1-based line numbers
    errors: List[str] = field(default_factory=list)


def summary(result: DeduplicateResult) -> str:
    lines = [
        f"Input rows   : {result.input_rows}",
        f"Output rows  : {result.output_rows}",
        f"Duplicates   : {result.duplicates_removed}",
    ]
    if result.duplicate_lines:
        lines.append(f"Dup at lines : {', '.join(str(n) for n in result.duplicate_lines)}")
    if result.errors:
        for err in result.errors:
            lines.append(f"ERROR        : {err}")
    return "\n".join(lines)


def deduplicate_csv(
    input_path: str,
    output_path: str,
    subset: Optional[List[str]] = None,
    keep: str = "first",
) -> DeduplicateResult:
    """Remove duplicate rows from a CSV file.

    Args:
        input_path: Path to the source CSV file.
        output_path: Path where deduplicated CSV will be written.
        subset: Column names to consider when detecting duplicates.
                If None, all columns are used.
        keep: 'first' keeps the first occurrence; 'last' keeps the last.

    Returns:
        DeduplicateResult with statistics about the operation.
    """
    result = DeduplicateResult()
    src = Path(input_path)

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    try:
        with src.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.errors.append("File is empty or has no header row.")
                return result

            fieldnames = list(reader.fieldnames)
            rows = list(reader)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"Failed to read file: {exc}")
        return result

    if subset:
        missing = [c for c in subset if c not in fieldnames]
        if missing:
            result.errors.append(f"Subset columns not found: {missing}")
            return result
        key_cols = subset
    else:
        key_cols = fieldnames

    result.input_rows = len(rows)

    seen: dict = {}
    for idx, row in enumerate(rows):
        key = tuple(row[c] for c in key_cols)
        if key not in seen:
            seen[key] = idx
        else:
            result.duplicate_lines.append(idx + 2)  # +1 header, +1 1-based

    if keep == "last":
        # Re-scan in reverse so last occurrence wins
        seen_last: dict = {}
        for idx, row in enumerate(reversed(rows)):
            key = tuple(row[c] for c in key_cols)
            if key not in seen_last:
                seen_last[key] = len(rows) - 1 - idx
        kept_indices = set(seen_last.values())
    else:
        kept_indices = set(seen.values())

    deduped = [row for idx, row in enumerate(rows) if idx in kept_indices]
    result.output_rows = len(deduped)
    result.duplicates_removed = result.input_rows - result.output_rows

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(deduped)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"Failed to write output: {exc}")

    return result
