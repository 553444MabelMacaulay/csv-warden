"""Rename columns by applying a prefix or suffix to all or selected columns."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PrefixSuffixResult:
    input_file: str
    output_file: str
    columns_renamed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        if not self.success:
            return f"ERROR: {'; '.join(self.errors)}"
        return (
            f"Renamed {len(self.columns_renamed)} column(s) in "
            f"'{self.input_file}' -> '{self.output_file}'"
        )


def apply_prefix_suffix(
    input_path: str,
    output_path: str,
    prefix: str = "",
    suffix: str = "",
    columns: Optional[list[str]] = None,
) -> PrefixSuffixResult:
    result = PrefixSuffixResult(input_file=input_path, output_file=output_path)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result
    if not prefix and not suffix:
        result.errors.append("At least one of prefix or suffix must be provided.")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no header row.")
            return result
        original_fields = list(reader.fieldnames)
        rows = list(reader)

    target = set(columns) if columns else set(original_fields)
    new_fields = []
    for col in original_fields:
        if col in target:
            new_col = f"{prefix}{col}{suffix}"
            result.columns_renamed.append(col)
        else:
            new_col = col
        new_fields.append(new_col)

    mapping = dict(zip(original_fields, new_fields))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=new_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({mapping[k]: v for k, v in row.items()})

    return result
