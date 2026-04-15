"""Helpers for loading consumption emissions KPI data."""
import pandas as pd

from facts.municipalities_counties import get_municipalities


SOURCE_PATH = "kpis/consumption/sources/Klimatkollen_data for 2023_shared April 2026.xlsx"


def get_consumption_emissions():
    """Extract consumption emissions data from source Excel file.

    Returns:
        pd.DataFrame: DataFrame with consumption emissions per 
                      territory in kg CO2e per capita with 4 decimals
    """
    consumption_df = pd.read_excel(SOURCE_PATH)

    consumption_df = consumption_df.rename(columns={"kommunnamn": "Kommun"})
    consumption_df = consumption_df.rename(
        columns={"Total_emissions_per_capita": "consumption_emissions"}
    )

    # Convert to kg CO2e per capita with 4 decimals
    consumption_df["consumption_emissions"] = (
        pd.to_numeric(consumption_df["consumption_emissions"], errors="coerce") / 1000
    )

    consumption_df = consumption_df[["Kommun", "consumption_emissions"]]
    municipality_names = set(get_municipalities()["Kommun"])
    consumption_df = consumption_df[consumption_df["Kommun"].isin(municipality_names)]

    return consumption_df
