import json
import pandas as pd
from pathlib import Path
from typing import Iterator


def _iter_consumption_entries() -> Iterator[dict]:
    """Yield all entries from consumption source JSON files."""
    sources_dir = Path(__file__).parent / "sources"
    for file_path in sources_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            yield from json.load(file)


def get_consumption_emissions():
    """Add consumption emissions data to the input DataFrame from source JSON files.

    Args:
        df (pd.DataFrame): Input DataFrame containing municipality data

    Returns:
        pd.DataFrame: DataFrame with consumption emissions data added
    """
    all_municipalities = []

    for entry in _iter_consumption_entries():
        # Skip entries for Sweden (SE) and counties (2-digit codes)
        if entry["code"] == "SE" or len(entry["code"]) <= 2:
            continue

        all_municipalities.append(
            {
                "Kommun": entry["name"],
                "consumptionEmissions": float(entry["emissions"]) / 1000,
            }
        )

    return pd.DataFrame(all_municipalities)


def get_regional_consumption_emissions() -> pd.DataFrame:
    """Load per-capita consumption emissions for Swedish län from source JSON files.

    Returns:
        pd.DataFrame: DataFrame with columns ``Län`` and ``consumptionEmissions``.
    """
    all_regions = []

    for entry in _iter_consumption_entries():
        if entry["code"] == "SE" or len(entry["code"]) > 2:
            continue

        all_regions.append(
            {
                "Län": entry["name"],
                "consumptionEmissions": float(entry["emissions"]) / 1000,
            }
        )

    return pd.DataFrame(all_regions)
