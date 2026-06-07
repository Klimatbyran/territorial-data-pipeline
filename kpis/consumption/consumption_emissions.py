"""Helpers for loading consumption emissions KPI data."""
import json
from pathlib import Path
from typing import Iterator

import pandas as pd

from facts.municipalities_counties import get_municipalities


SOURCE_PATH = "kpis/consumption/sources/Klimatkollen_data for 2023_shared April 2026.xlsx"
JSON_SOURCES_DIR = Path(__file__).parent / "sources"


def _iter_consumption_json_entries() -> Iterator[dict]:
    """Yield all entries from regional consumption JSON source files."""
    for file_path in JSON_SOURCES_DIR.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            yield from json.load(file)


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


def get_regional_consumption_emissions() -> pd.DataFrame:
    """Load per-capita consumption emissions for Swedish län from JSON source files.

    Returns:
        pd.DataFrame: DataFrame with columns ``Län`` and ``consumption_emissions``.
    """
    all_regions = []

    for entry in _iter_consumption_json_entries():
        if entry["code"] == "SE" or len(entry["code"]) > 2:
            continue

        all_regions.append(
            {
                "Län": entry["name"],
                "consumption_emissions": float(entry["emissions"]) / 1000,
            }
        )

    return pd.DataFrame(all_regions)
