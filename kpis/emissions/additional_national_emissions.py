# -*- coding: utf-8 -*-
"""Load supplementary national emission series from the PowerCircle / planning workbook."""

from __future__ import annotations
from typing import Any, Optional
import pandas as pd

PATH_ADDITIONAL_NATIONAL_EMISSIONS = (
    "kpis/emissions/sources/additional_national_emissions.xlsx"
)
SHEET_ALLA = "Alla"
HEADER_VARIABEL = "Variabel"

COLUMN_NAMES: dict[str, str] = {
    "Terr_CO2e_bio": "biogenic",
    "Kons_utlandet": "consumption",
    "Export av oljeprodukter": "export_of_oil_products",
}


def _parse_numeric_cell(value: Any) -> float:
    """Parse Excel cell values: Swedish space-separated thousands, or plain numbers."""
    if pd.isna(value):
        return float("nan")
    text_value = str(value).strip().replace(" ", "")
    float_value = float(text_value)
    return float_value

def load_additional_national_emissions(
    path: str = PATH_ADDITIONAL_NATIONAL_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Load the summary sheet where each row is a variable and columns are calendar years.

    Returns:
        DataFrame indexed by variable name (string), columns are int years, values are float.
    """
    source_df = pd.read_excel(path, sheet_name=sheet_name, header=None)

    # Drop metadata rows above the header, promote the Variabel row as column names
    source_df = source_df.drop(range(4)).reset_index(drop=True)
    source_df.columns = source_df.iloc[0]
    source_df = source_df.drop(0).reset_index(drop=True)

    # Set variable names as the index
    source_df = source_df.set_index("Variabel")
    source_df.index.name = None

    # Keep only the desired year columns, cast to int
    year_cols = list(range(1990, 2025))
    source_df = source_df[[c for c in source_df.columns if int(c) in year_cols]]
    source_df.columns = [int(c) for c in source_df.columns]

    # Parse all values in place
    source_df = source_df.map(_parse_numeric_cell)

    return source_df


def merge_additional_national_emissions_into_national_df(
    national_df: pd.DataFrame,
    summary_df: Optional[pd.DataFrame] = None,
    path: str = PATH_ADDITIONAL_NATIONAL_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Add flattened columns from the additional national summary to the national dataframe.

    For each variable and year in the summary, adds one column
    ``<variable>_<year>``.
    """
    if summary_df is None:
        summary_df = load_additional_national_emissions(path, sheet_name)

    out = national_df.copy()

    additional_emissions = {}
    for variable in summary_df.index:
        if variable not in COLUMN_NAMES:
            continue
        slug = COLUMN_NAMES[variable]
        for year in summary_df.columns:
            col_name = f"{slug}_{year}"
            additional_emissions[col_name] = summary_df.loc[variable, year]

    concat_df = pd.concat(
        [out, pd.DataFrame([additional_emissions] * len(out)).reset_index(drop=True)],
        axis=1
    )
    return concat_df