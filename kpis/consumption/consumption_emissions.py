"""Helpers for loading consumption emissions KPI data."""
import pandas as pd

from facts.municipalities_counties import get_municipalities


SOURCE_PATH = "kpis/consumption/sources/Klimatkollen_data for 2023_shared April 2026.xlsx"
MUNICIPAL_SHEET = "Municipal_grouped"
COUNTY_SHEET = "County_grouped"


def _load_consumption_from_excel(sheet_name: str) -> pd.DataFrame:
    """Load per-capita consumption emissions from a sheet in the source Excel file."""
    consumption_df = pd.read_excel(SOURCE_PATH, sheet_name=sheet_name)

    consumption_df = consumption_df.rename(
        columns={"Total_emissions_per_capita": "consumption_emissions"}
    )
    consumption_df["consumption_emissions"] = (
        pd.to_numeric(consumption_df["consumption_emissions"], errors="coerce") / 1000
    )

    return consumption_df


def get_consumption_emissions():
    """Extract consumption emissions data from source Excel file.

    Returns:
        pd.DataFrame: DataFrame with consumption emissions per
                      territory in tonnes CO2e per capita.
    """
    consumption_df = _load_consumption_from_excel(MUNICIPAL_SHEET)
    consumption_df = consumption_df.rename(columns={"kommunnamn": "Kommun"})
    consumption_df = consumption_df[["Kommun", "consumption_emissions"]]

    municipality_names = set(get_municipalities()["Kommun"])
    consumption_df = consumption_df[consumption_df["Kommun"].isin(municipality_names)]

    return consumption_df


def get_regional_consumption_emissions() -> pd.DataFrame:
    """Load per-capita consumption emissions for Swedish län from the Excel source.

    Returns:
        pd.DataFrame: DataFrame with columns ``Län`` and ``consumption_emissions``.
    """
    consumption_df = _load_consumption_from_excel(COUNTY_SHEET)
    consumption_df = consumption_df.rename(columns={"kommunnamn": "Län"})
    consumption_df = consumption_df[["Län", "consumption_emissions"]]

    region_names = set(get_municipalities()["Län"].unique())
    consumption_df = consumption_df[consumption_df["Län"].isin(region_names)]

    return consumption_df
