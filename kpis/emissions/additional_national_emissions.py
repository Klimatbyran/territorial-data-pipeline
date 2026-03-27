# -*- coding: utf-8 -*-
"""Load supplementary national emission series from the PowerCircle / planning workbook."""

from __future__ import annotations

import re
from typing import Any, Optional

import pandas as pd

PATH_ADDITIONAL_NATIONAL_EMISSIONS = (
    "kpis/emissions/sources/additional_national_emissions.xlsx"
)
SHEET_ALLA = "Alla"
HEADER_VARIABEL = "Variabel"


def _parse_numeric_cell(value: Any) -> float:
    """Parse Excel cell values: Swedish space-separated thousands, or plain numbers."""
    if pd.isna(value):
        return float("nan")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip().replace("\u00a0", " ")
    text = re.sub(r"\s+", "", text)
    return float(text)


def _safe_column_name(variable: str, year: int) -> str:
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", variable.strip()).strip("_")
    return f"additional_national_{slug}_{year}"


def load_additional_national_emissions_summary(
    path: str = PATH_ADDITIONAL_NATIONAL_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Load the summary sheet where each row is a variable and columns are calendar years.

    Returns:
        DataFrame indexed by variable name (string), columns are int years, values are float.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)

    header_row_idx: Optional[int] = None
    for i in range(len(raw)):
        cell = raw.iloc[i, 0]
        if pd.notna(cell) and str(cell).strip() == HEADER_VARIABEL:
            header_row_idx = i
            break
    if header_row_idx is None:
        raise ValueError(
            f"Could not find '{HEADER_VARIABEL}' header row in {path!r} sheet {sheet_name!r}"
        )

    year_cols: list[tuple[int, int]] = []
    for col_idx in range(1, raw.shape[1]):
        cell = raw.iloc[header_row_idx, col_idx]
        if pd.isna(cell):
            continue
        year_cols.append((col_idx, int(float(cell))))

    rows: dict[str, dict[int, float]] = {}
    for row_idx in range(header_row_idx + 1, len(raw)):
        name = raw.iloc[row_idx, 0]
        if pd.isna(name) or str(name).strip() == "":
            continue
        var = str(name).strip()
        rows[var] = {}
        for col_idx, year in year_cols:
            rows[var][year] = _parse_numeric_cell(raw.iloc[row_idx, col_idx])

    if not rows:
        raise ValueError("No data rows found below the Variabel header")

    all_years = sorted({y for d in rows.values() for y in d})
    index = list(rows.keys())
    data = {year: [rows[v].get(year, float("nan")) for v in index] for year in all_years}
    return pd.DataFrame(data, index=index)


def merge_additional_national_emissions_into_national_df(
    national_df: pd.DataFrame,
    summary_df: Optional[pd.DataFrame] = None,
    path: str = PATH_ADDITIONAL_NATIONAL_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Add flattened columns from the additional national summary to the national dataframe.

    For each variable and year in the summary, adds one column
    ``additional_national_<slug>_<year>`` aligned to ``Land`` (one row per country).
    """
    if summary_df is None:
        summary_df = load_additional_national_emissions_summary(path, sheet_name)

    out = national_df.copy()
    if "Land" not in out.columns:
        raise ValueError("national_df must contain a 'Land' column")

    extra = {}
    for variable in summary_df.index:
        for year in summary_df.columns:
            col_name = _safe_column_name(variable, int(year))
            extra[col_name] = summary_df.loc[variable, year]
    return pd.concat([out, pd.DataFrame([extra] * len(out)).reset_index(drop=True)], axis=1)
