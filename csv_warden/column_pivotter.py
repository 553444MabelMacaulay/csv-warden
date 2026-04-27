"""column_pivotter.py — reshape a CSV by pivoting a single column's unique
values into new columns (wide format), with an optional aggregation function.

This is a *column-level* pivot that works on a key column + value column pair,
producing one output column per unique value found in the key column.
"""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ColPivotResult:
    input_file: str
    output_file: str
    index_col: str
    key_col: str
    value_col: str
    aggfunc: str
    new_columns: List[str] = field(default_factory=list)
    rows_written: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def summary(result: ColPivotResult) -> str:
    lines = [
        f"Input  : {result.input_file}",
        f"Output : {result.output_file}",
        f"Index  : {result.index_col}",
        f"Key    : {result.key_col}  →  {len(result.new_columns)} new column(s)",
        f"Value  : {result.value_col}  (aggfunc={result.aggfunc})",
        f"Rows written : {result.rows_written}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    else:
        lines.append("Status : OK")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _agg_first(values: List[str]) -> str:
    return values[0] if values else ""


def _agg_last(values: List[str]) -> str:
    return values[-1] if values else ""


def _agg_count(values: List[str]) -> str:
    return str(len(values))


def _agg_sum(values: List[str]) -> str:
    try:
        return str(sum(float(v) for v in values if v != ""))
    except ValueError:
        return ""


def _agg_mean(values: List[str]) -> str:
    nums = [float(v) for v in values if v != ""]
    if not nums:
        return ""
    return str(sum(nums) / len(nums))


_AGGFUNCS: Dict[str, Callable[[List[str]], str]] = {
    "first": _agg_first,
    "last": _agg_last,
    "count": _agg_count,
    "sum": _agg_sum,
    "mean": _agg_mean,
}


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def col_pivot_csv(
    input_file: str,
    output_file: str,
    index_col: str,
    key_col: str,
    value_col: str,
    aggfunc: str = "first",
) -> ColPivotResult:
    """Pivot *key_col* unique values into new columns, aggregating *value_col*.

    Parameters
    ----------
    input_file:  path to the source CSV.
    output_file: path where the pivoted CSV will be written.
    index_col:   column whose values become row identifiers.
    key_col:     column whose unique values become new column headers.
    value_col:   column whose values are placed in the pivoted cells.
    aggfunc:     one of ``first | last | count | sum | mean``.
    """
    result = ColPivotResult(
        input_file=input_file,
        output_file=output_file,
        index_col=index_col,
        key_col=key_col,
        value_col=value_col,
        aggfunc=aggfunc,
    )

    if not os.path.exists(input_file):
        result.errors.append(f"File not found: {input_file}")
        return result

    if aggfunc not in _AGGFUNCS:
        result.errors.append(
            f"Unknown aggfunc '{aggfunc}'. Choose from: {', '.join(_AGGFUNCS)}"
        )
        return result

    agg_fn = _AGGFUNCS[aggfunc]

    # First pass — collect all data into a nested dict:
    #   pivot_data[index_value][key_value] = [val1, val2, ...]
    pivot_data: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    key_order: List[str] = []  # preserve insertion order of keys
    index_order: List[str] = []  # preserve insertion order of index values

    try:
        with open(input_file, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.errors.append("CSV has no header row.")
                return result

            headers = list(reader.fieldnames)
            for required in (index_col, key_col, value_col):
                if required not in headers:
                    result.errors.append(f"Column not found: '{required}'")
            if result.errors:
                return result

            for row in reader:
                idx = row[index_col]
                key = row[key_col]
                val = row[value_col]

                if idx not in index_order:
                    index_order.append(idx)
                if key not in key_order:
                    key_order.append(key)

                pivot_data[idx][key].append(val)

    except OSError as exc:
        result.errors.append(str(exc))
        return result

    result.new_columns = key_order

    # Second pass — write pivoted output
    out_headers = [index_col] + key_order
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=out_headers)
            writer.writeheader()
            for idx in index_order:
                row_out: Dict[str, str] = {index_col: idx}
                for key in key_order:
                    values = pivot_data[idx].get(key, [])
                    row_out[key] = agg_fn(values)
                writer.writerow(row_out)
                result.rows_written += 1
    except OSError as exc:
        result.errors.append(str(exc))
        return result

    return result
