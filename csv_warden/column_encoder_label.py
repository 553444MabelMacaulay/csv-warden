"""Label encoder for categorical columns in CSV files.

Assigns a unique integer to each distinct value in a column,
writing the encoded values to a new or replacement column.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LabelEncodeResult:
    input_file: str
    output_file: str
    column: str
    mapping: Dict[str, int] = field(default_factory=dict)
    rows_encoded: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: LabelEncodeResult) -> str:
    lines = [
        f"Input  : {result.input_file}",
        f"Output : {result.output_file}",
        f"Column : {result.column}",
        f"Rows encoded : {result.rows_encoded}",
    ]
    if result.mapping:
        lines.append("Label mapping:")
        for label, code in sorted(result.mapping.items(), key=lambda x: x[1]):
            lines.append(f"  {code} -> {label!r}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def label_encode_csv(
    input_path: str,
    output_path: str,
    column: str,
    new_column: Optional[str] = None,
    drop_original: bool = False,
) -> LabelEncodeResult:
    """Label-encode *column* and write results to *output_path*.

    Parameters
    ----------
    input_path:
        Path to the source CSV.
    output_path:
        Path where the encoded CSV will be written.
    column:
        Name of the column to encode.
    new_column:
        Name for the encoded column.  Defaults to ``<column>_label``.
        When equal to *column* the original column is replaced in-place.
    drop_original:
        If *True* and *new_column* differs from *column*, the original
        column is removed from the output.
    """
    src = Path(input_path)
    result = LabelEncodeResult(
        input_file=input_path,
        output_file=output_path,
        column=column,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    encoded_col = new_column if new_column else f"{column}_label"
    replace_in_place = encoded_col == column

    # --- first pass: build the mapping in encounter order ---
    mapping: Dict[str, int] = {}
    try:
        with src.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or column not in (reader.fieldnames or []):
                result.errors.append(f"Column not found: {column}")
                return result
            for row in reader:
                val = row[column]
                if val not in mapping:
                    mapping[val] = len(mapping)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"Read error: {exc}")
        return result

    result.mapping = mapping

    # --- second pass: write encoded output ---
    try:
        with src.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            original_fields: List[str] = list(reader.fieldnames or [])

            # Build output fieldnames
            if replace_in_place:
                out_fields = original_fields
            elif drop_original:
                out_fields = [f for f in original_fields if f != column] + [encoded_col]
            else:
                out_fields = original_fields + [encoded_col]

            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)

            with out_path.open("w", newline="", encoding="utf-8") as out_fh:
                writer = csv.DictWriter(out_fh, fieldnames=out_fields, extrasaction="ignore")
                writer.writeheader()
                for row in reader:
                    encoded_val = str(mapping.get(row[column], ""))
                    if replace_in_place:
                        row[column] = encoded_val
                    else:
                        row[encoded_col] = encoded_val
                    writer.writerow(row)
                    result.rows_encoded += 1
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"Write error: {exc}")

    return result
