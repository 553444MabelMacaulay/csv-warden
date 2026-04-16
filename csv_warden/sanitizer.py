"""Sanitization utilities for CSV files."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class SanitizeResult:
    rows_read: int = 0
    rows_written: int = 0
    cells_modified: int = 0
    rows_dropped: int = 0
    changes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Rows read    : {self.rows_read}",
            f"Rows written : {self.rows_written}",
            f"Rows dropped : {self.rows_dropped}",
            f"Cells modified: {self.cells_modified}",
        ]
        if self.changes:
            lines.append("Changes:")
            for c in self.changes[:10]:
                lines.append(f"  {c}")
            if len(self.changes) > 10:
                lines.append(f"  ... and {len(self.changes) - 10} more")
        return "\n".join(lines)


def _strip_whitespace(value: str) -> str:
    return value.strip()


def _normalize_empty(value: str) -> str:
    """Replace blank/whitespace-only cells with empty string."""
    return "" if value.strip() == "" else value


def sanitize_csv(
    source: str | Path,
    dest: Optional[str | Path] = None,
    *,
    strip_whitespace: bool = True,
    normalize_empty: bool = True,
    drop_empty_rows: bool = True,
    extra_transforms: Optional[Dict[str, Callable[[str], str]]] = None,
) -> SanitizeResult:
    """Read *source*, apply sanitization rules, write to *dest* (or overwrite source).

    Args:
        source: Path to the input CSV file.
        dest: Path for the output CSV file. Defaults to overwriting *source*.
        strip_whitespace: Strip leading/trailing whitespace from every cell.
        normalize_empty: Normalize whitespace-only cells to empty strings.
        drop_empty_rows: Drop rows where every cell is empty after transforms.
        extra_transforms: Optional per-column transform functions keyed by
            column header name.

    Returns:
        A :class:`SanitizeResult` describing what was changed.

    Raises:
        FileNotFoundError: If *source* does not exist.
        ValueError: If *source* is not a valid CSV file.
    """
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    dest = Path(dest) if dest else source
    extra_transforms = extra_transforms or {}

    result = SanitizeResult()
    output_rows: List[List[str]] = []
    header: List[str] = []

    with source.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                output_rows.append(row)
                continue

            result.rows_read += 1
            new_row: List[str] = []
            for col_idx, cell in enumerate(row):
                original = cell
                col_name = header[col_idx] if col_idx < len(header) else str(col_idx)

                if strip_whitespace:
                    cell = _strip_whitespace(cell)
                if normalize_empty:
                    cell = _normalize_empty(cell)
                if col_name in extra_transforms:
                    cell = extra_transforms[col_name](cell)

                if cell != original:
                    result.cells_modified += 1
                    result.changes.append(
                        f"row {i + 1}, col '{col_name}': {original!r} -> {cell!r}"
                    )
                new_row.append(cell)

            if drop_empty_rows and all(c == "" for c in new_row):
                result.rows_dropped += 1
                continue

            output_rows.append(new_row)
            result.rows_written += 1

    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows(output_rows)

    return result
