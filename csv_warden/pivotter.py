from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import csv
from pathlib import Path
from typing import Optional


@dataclass
class PivotResult:
    input_file: str
    output_file: str
    index_column: str
    pivot_column: str
    value_column: str
    rows_read: int = 0
    rows_written: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: PivotResult) -> str:
    lines = [
        f"Input:         {r.input_file}",
        f"Output:        {r.output_file}",
        f"Index column:  {r.index_column}",
        f"Pivot column:  {r.pivot_column}",
        f"Value column:  {r.value_column}",
        f"Rows read:     {r.rows_read}",
        f"Rows written:  {r.rows_written}",
    ]
    if r.errors:
        lines.append("Errors:")
        for e in r.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def pivot_csv(
    input_path: str,
    output_path: str,
    index_column: str,
    pivot_column: str,
    value_column: str,
    aggfunc: str = "first",
) -> PivotResult:
    result = PivotResult(
        input_file=input_path,
        output_file=output_path,
        index_column=index_column,
        pivot_column=pivot_column,
        value_column=value_column,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    # data[index_val][pivot_val] -> list of values
    data: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    pivot_values: set[str] = set()

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header")
            return result
        for required in (index_column, pivot_column, value_column):
            if required not in reader.fieldnames:
                result.errors.append(f"Column not found: {required}")
        if result.errors:
            return result
        for row in reader:
            result.rows_read += 1
            idx = row[index_column]
            piv = row[pivot_column]
            val = row[value_column]
            pivot_values.add(piv)
            data[idx][piv].append(val)

    sorted_pivots = sorted(pivot_values)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([index_column] + sorted_pivots)
        for idx_val, piv_map in sorted(data.items()):
            row_out = [idx_val]
            for piv in sorted_pivots:
                vals = piv_map.get(piv, [])
                if not vals:
                    cell = ""
                elif aggfunc == "sum":
                    try:
                        cell = str(sum(float(v) for v in vals))
                    except ValueError:
                        cell = vals[0]
                elif aggfunc == "count":
                    cell = str(len(vals))
                else:
                    cell = vals[0]
                row_out.append(cell)
            writer.writerow(row_out)
            result.rows_written += 1

    return result
