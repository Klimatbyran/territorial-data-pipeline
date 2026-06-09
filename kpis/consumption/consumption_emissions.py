"""Helpers for loading consumption emissions KPI data."""
import pandas as pd

from facts.municipalities_counties import get_municipalities


SOURCE_PATH = "kpis/consumption/sources/Klimatkollen_data for 2023_shared April 2026.xlsx"
MUNICIPAL_SHEET = "Municipal_grouped"


def get_consumption_emissions():
    """Extract municipal consumption emissions from the Klimatkollen Excel source.

    Returns:
        pd.DataFrame: DataFrame with consumption emissions per municipality
                      in tonnes CO2e per capita.
    """
    consumption_df = pd.read_excel(SOURCE_PATH, sheet_name=MUNICIPAL_SHEET)

    consumption_df = consumption_df.rename(columns={"kommunnamn": "Kommun"})
    consumption_df = consumption_df.rename(
        columns={"Total_emissions_per_capita": "consumption_emissions"}
    )
    consumption_df["consumption_emissions"] = (
        pd.to_numeric(consumption_df["consumption_emissions"], errors="coerce") / 1000
    )

    consumption_df = consumption_df[["Kommun", "consumption_emissions"]]
    municipality_names = set(get_municipalities()["Kommun"])
    consumption_df = consumption_df[consumption_df["Kommun"].isin(municipality_names)]

    return consumption_df
