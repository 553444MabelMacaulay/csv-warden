"""Merge multiple CSV files into a single output CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class MergeResult:
    input_files: List[str] = field(default_factory=list)
    output_file: str = ""
    total_rows_written: int = 0
    skipped_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def summary(result: MergeResult) -> str:
    lines = [
        f"Merge Summary",
        f"  Input files   : {len(result.input_files)}",
        f"  Skipped files : {len(result.skipped_files)}",
        f"  Rows written  : {result.total_rows_written}",
        f"  Output        : {result.output_file}",
    ]
    if result.errors:
        lines.append("  Errors:")
        for err in result.errors:
            lines.append(f"    - {err}")
    return "\n".join(lines)


def merge_csv(
    input_paths: List[str],
    output_path: str,
    require_same_columns: bool = True,
) -> MergeResult:
    """Merge multiple CSV files into *output_path*.

    Parameters
    ----------
    input_paths:
        Ordered list of CSV file paths to merge.
    output_path:
        Destination file for the merged output.
    require_same_columns:
        When True, files whose headers differ from the first file are skipped
        and recorded in ``result.skipped_files``.
    """
    result = MergeResult(output_file=output_path)
    reference_header: Optional[List[str]] = None
    rows_buffer: List[dict] = []

    for path_str in input_paths:
        path = Path(path_str)
        if not path.exists():
            result.errors.append(f"File not found: {path_str}")
            result.skipped_files.append(path_str)
            continue

        try:
            with path.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    result.errors.append(f"Empty or header-less file: {path_str}")
                    result.skipped_files.append(path_str)
                    continue

                header = list(reader.fieldnames)

                if reference_header is None:
                    reference_header = header
                elif require_same_columns and header != reference_header:
                    result.errors.append(
                        f"Column mismatch in '{path_str}': "
                        f"expected {reference_header}, got {header}"
                    )
                    result.skipped_files.append(path_str)
                    continue

                result.input_files.append(path_str)
                for row in reader:
                    rows_buffer.append(row)
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Could not read '{path_str}': {exc}")
            result.skipped_files.append(path_str)

    if reference_header is None:
        result.errors.append("No valid input files to merge.")
        return result

    with Path(output_path).open("w", newline="", encoding="utf-8") as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=reference_header)
        writer.writeheader()
        writer.writerows(rows_buffer)

    result.total_rows_written = len(rows_buffer)
    return result
