# -*- coding: utf-8 -*-
"""Load national emission series."""

from __future__ import annotations
from datetime import datetime
from typing import Any
import pandas as pd

from kpis.emissions.carbon_law_calculations import calculate_carbon_law_total
from kpis.emissions.emission_data_calculations import calculate_historical_change_percent, calculate_meets_paris_goal
from kpis.emissions.trend_calculations import calculate_trend


CURRENT_YEAR = datetime.now().year  # current year
END_YEAR = 2050

CARBON_LAW_REDUCTION_RATE = 0.1172

LAST_YEAR_WITH_SMHI_DATA = 2023

PATH_LOAD_SWEDISH_EMISSIONS = (
    "kpis/emissions/sources/swedish_emissions.xlsx"
)
SHEET_ALLA = "Alla"
HEADER_VARIABEL = "Variabel"

COLUMN_NAMES: dict[str, str] = {
    "Terr_CO2e_foss": "fossil",
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

    emissions = {}
    for variable in summary_df.index:
        if variable not in COLUMN_NAMES:
            continue
        slug = COLUMN_NAMES[variable]
        for year in summary_df.columns:
            col_name = f"{slug}_{year}"
            emissions[col_name] = summary_df.loc[variable, year]

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
        year_cols = [col for col in emissions_df.columns if col.endswith(f"_{year}")]
        emissions_df[f"total_{year}"] = emissions_df[year_cols].sum(axis=1)

    return emissions_df

def create_swedish_emissions_df():
    """
    Create a dataframe with emissions per year for Sweden
    (territorial, biogenic, consumption, export of oil products, total).
    Also add KPIs (trend, historical change percent, carbon law path, meets Paris goal).

    Returns:
        pandas.DataFrame: The resulting dataframe with emissions per year and KPIs.
    """
    emissions_df = _extract_emissions()

    emissions_df = _calculate_total_emissions(emissions_df)

    df_trend_and_approximated = calculate_trend(emissions_df, CURRENT_YEAR, END_YEAR)

    df_trend_and_approximated["total_trend"] = df_trend_and_approximated.apply(
        lambda row: row[[col for col in row.index if "trend_" in str(col)]].sum(),
        axis=1,
    )

    df_historical_change_percent = calculate_historical_change_percent(
        df_trend_and_approximated, "Land", LAST_YEAR_WITH_SMHI_DATA
    )

    df_carbon_law = calculate_carbon_law_total(
        df_historical_change_percent,
        CURRENT_YEAR,
        END_YEAR,
        CARBON_LAW_REDUCTION_RATE,
    )

    df_carbon_law["meetsParisGoal"] = df_carbon_law.apply(
        lambda row: calculate_meets_paris_goal(
            row["total_trend"], row["totalCarbonLawPath"]
        ),
        axis=1,
    )

    return df_carbon_law
