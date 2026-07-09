# -*- coding: utf-8 -*-
"""Load national emission series."""

from __future__ import annotations
from typing import Any
import pandas as pd

PATH_LOAD_SWEDISH_EMISSIONS = (
    "kpis/emissions/sources/swedish_emissions.xlsx"
)
SHEET_ALLA = "Alla"
SHEET_E_HANDEL = "E-handel"
SHEET_TERR_GHG = "Terr_GHG"
HEADER_VARIABEL = "Variabel"
NATIONAL_TERRITORIAL_ROW = "Alla_NV"
E_HANDEL_YEARS = list(range(2020, 2026))
LAST_YEAR = 2025

COLUMN_NAMES: dict[str, str] = {
    "Terr_CO2e_foss": "fossil",
    "Produktionsbaserade utsläpp": "production_based",
    "Terr_CO2e_bio": "biogenic",
    "Biogena utsläpp": "biogenic",
    "Kons_utlandet": "consumption",
    "Konsumtionsbaserade utsläpp i utlandet": "consumption",
    "Export av oljeprodukter": "export_of_oil_products",
    "Utsläpp i utlandet pga export av oljeprodukter": "export_of_oil_products",
}


def _parse_numeric_cell(value: Any) -> float:
    """Parse Excel cell values: Swedish space-separated thousands, or plain numbers."""
    if pd.isna(value):
        return float("nan")
    text_value = str(value).strip().replace(" ", "")
    float_value = float(text_value)
    return float_value


def _year_columns(columns: pd.Index) -> list[int]:
    """Return sorted integer year columns from a mixed header row."""
    years = []
    for column in columns:
        if pd.isna(column):
            continue
        text = str(column).strip()
        if text.endswith(".0"):
            text = text[:-2]
        if text.isdigit() and len(text) == 4:
            years.append(int(text))
    return sorted(set(years))


def _load_swedish_emissions_source(
    path: str = PATH_LOAD_SWEDISH_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Load the summary sheet where each row is a variable and columns are calendar years.

    Returns:
        DataFrame indexed by variable name (string), columns are int years, values are float.
    """
    source_df = pd.read_excel(path, sheet_name=sheet_name, header=None)
    header_row_idx = source_df.index[source_df.iloc[:, 0] == HEADER_VARIABEL][0]
    source_df = source_df.iloc[header_row_idx:].reset_index(drop=True)
    source_df.columns = source_df.iloc[0]
    source_df = source_df.drop(0).reset_index(drop=True)

    year_cols = [
        year
        for year in _year_columns(source_df.columns)
        if 1990 <= year <= LAST_YEAR
    ]
    variable_col = source_df.columns[0]
    selected_cols = [variable_col] + [
        col
        for col in source_df.columns
        if _year_columns([col]) and _year_columns([col])[0] in year_cols
    ]
    source_df = source_df[selected_cols]
    source_df = source_df.set_index(variable_col)
    source_df.index.name = None
    source_df = source_df.loc[source_df.index.notna()]
    source_df.columns = [_year_columns([col])[0] for col in source_df.columns]
    source_df = source_df.map(_parse_numeric_cell)

    return source_df


def _load_territorial_emissions_source(
    path: str = PATH_LOAD_SWEDISH_EMISSIONS,
    sheet_name: str = SHEET_TERR_GHG,
) -> pd.Series:
    """
    Load national territorial GHG emissions from the Terr_GHG sheet.

    Returns:
        Series indexed by year with float emission values.
    """
    source_df = pd.read_excel(path, sheet_name=sheet_name, header=None)
    header_row_idx = next(
        idx
        for idx in range(len(source_df))
        if 1990 in _year_columns(source_df.iloc[idx])
    )
    country_row_idx = source_df.index[
        source_df.iloc[:, 3] == NATIONAL_TERRITORIAL_ROW
    ][0]

    year_positions = {
        idx: _year_columns([source_df.iloc[header_row_idx, idx]])[0]
        for idx in range(len(source_df.columns))
        if _year_columns([source_df.iloc[header_row_idx, idx]])
        and 1990 <= _year_columns([source_df.iloc[header_row_idx, idx]])[0] <= LAST_YEAR
    }

    values = {
        year: _parse_numeric_cell(source_df.iloc[country_row_idx, col_idx])
        for col_idx, year in year_positions.items()
    }
    return pd.Series(values)


def _load_e_handel_emissions_source(
    path: str = PATH_LOAD_SWEDISH_EMISSIONS,
    sheet_name: str = SHEET_E_HANDEL,
) -> pd.DataFrame:
    """
    Load the E-handel sheet with one national row and year columns 2020–2025.

    Returns:
        DataFrame indexed by country name, columns are int years, values are float.
    """
    source_df = pd.read_excel(path, sheet_name=sheet_name, header=None)
    country_row_idx = source_df.index[source_df.iloc[:, 0] == "Sverige"][0]
    year_row_idx = country_row_idx - 1
    while year_row_idx >= 0 and not _year_columns(source_df.iloc[year_row_idx]):
        year_row_idx -= 1

    years = [
        year
        for year in _year_columns(source_df.iloc[year_row_idx])
        if year in E_HANDEL_YEARS
    ]
    year_positions = {
        idx: int(str(source_df.iloc[year_row_idx, idx]).replace(".0", ""))
        for idx in range(len(source_df.columns))
        if pd.notna(source_df.iloc[year_row_idx, idx])
        and str(source_df.iloc[year_row_idx, idx]).replace(".0", "").isdigit()
        and int(str(source_df.iloc[year_row_idx, idx]).replace(".0", "")) in E_HANDEL_YEARS
    }

    values = {
        year: _parse_numeric_cell(source_df.iloc[country_row_idx, col_idx])
        for col_idx, year in year_positions.items()
    }
    return pd.DataFrame([values], index=["Sverige"])


def _extract_emissions(
    path: str = PATH_LOAD_SWEDISH_EMISSIONS,
    sheet_name: str = SHEET_ALLA,
) -> pd.DataFrame:
    """
    Create a dataframe with flattened columns from the Swedish emissions summary.

    For each variable and year in the summary, adds one column
    ``<variable>_<year>``.
    """
    summary_df = _load_swedish_emissions_source(path, sheet_name)
    territorial_df = _load_territorial_emissions_source(path)

    emissions = {}
    for year, value in territorial_df.items():
        emissions[f"fossil_{year}"] = value

    for variable in summary_df.index:
        if variable not in COLUMN_NAMES:
            continue
        slug = COLUMN_NAMES[variable]
        for year in summary_df.columns:
            col_name = f"{slug}_{year}"
            emissions[col_name] = summary_df.loc[variable, year]

    e_handel_df = _load_e_handel_emissions_source(path, SHEET_E_HANDEL)
    for year in e_handel_df.columns:
        emissions[f"e_commerce_{year}"] = e_handel_df.loc["Sverige", year]

    emissions_df = pd.DataFrame([emissions])

    return emissions_df


def _calculate_total_emissions(emissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the total emissions per year for the given dataframe.

    Returns:
        pandas.DataFrame: The resulting dataframe with total emissions per year.
    """
    years = sorted({int(col.rsplit("_", 1)[-1]) for col in emissions_df.columns})
    for year in years:
        year_cols = [
            col
            for col in emissions_df.columns
            if col.endswith(f"_{year}") and not col.startswith("fossil_")
        ]
        emissions_df[f"total_{year}"] = emissions_df[year_cols].sum(axis=1)

    return emissions_df


def create_swedish_emissions_df():
    """
    Create a dataframe with emissions per year for Sweden
    (territorial, biogenic, consumption, export of oil products, e-commerce, total).

    Returns:
        pandas.DataFrame: The resulting dataframe with emissions per year.
    """
    emissions_df = _extract_emissions()
    emissions_df = _calculate_total_emissions(emissions_df)
    emissions_df["Land"] = "Sverige"
    return emissions_df
