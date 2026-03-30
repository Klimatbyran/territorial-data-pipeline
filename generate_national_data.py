# -*- coding: utf-8 -*-
"""Generate national climate data JSON from emissions calculations and supplementary sources."""

import argparse
import json
from typing import Any, Dict, List

import pandas as pd

from facts.coatOfArms.coat_of_arms import get_coat_of_arms
from kpis.emissions.swedish_emissions import (
    _extract_emissions,
)
from kpis.emissions.national_emissions import national_emission_calculations

def create_national_dataframe() -> pd.DataFrame:
    """Create a comprehensive national climate dataframe by merging multiple data sources"""

    national_df = national_emission_calculations()
    print("1. National climate data and calculations added")

    national_df["Land"] = "Sverige"
    print("2. Set country name to 'Sverige'")

    national_df["coatOfArms"] = national_df["Land"].apply(get_coat_of_arms)
    print("2. Coat of arms added")

    # TODO
    # political_rule_df = get_political_rule()
    # result_df = emissions_df.merge(political_rule_df, on="Land", how="left")
    # print("2. Political rule added")

    return national_df


def series_to_dict(row: pd.Series, column_groups: Dict[str, List[Any]]) -> Dict:
    """
    Transforms a pandas Series into a dictionary.

    Args:
        row: The pandas Series to transform.
        column_groups: Named lists of column keys grouped by emission type.

    Returns:
        A dictionary with the transformed data.
    """
    return {
        "country": row["Land"],
        "logoUrl": row["coatOfArms"],
        "territorialFossilEmissions": {
            str(year.strip("fossil_")): row[year]
            for year in column_groups["fossil"]
        },
        "biogenicEmissions": {
            str(year.strip("biogenic_")): row[year]
            for year in column_groups["biogenic"]
        },
        "consumptionAbroadEmissions": {
            str(year.strip("consumption_")): row[year]
            for year in column_groups["consumption"]
        },
        "exportOfOilProductsEmissions": {
            str(year.strip("export_of_oil_products_")): row[year]
            for year in column_groups["export_of_oil_products"]
        },
        "totalTrend": row["total_trend"],
        "totalCarbonLaw": row["totalCarbonLawPath"],
        "approximatedHistoricalEmission": {
            year.replace("approximated_", ""): row[year]
            for year in column_groups["approximated"]
        },
        "trend": {
            year.replace("trend_", ""): row[year]
            for year in column_groups["trend"]
        },
        "emissionsSlope": row["trend_emissions_slope"],
        "historicalEmissionChangePercent": row["historicalEmissionChangePercent"],
        "meetsParis": row["total_trend"] / row["totalCarbonLawPath"] < 1,
    }


def df_to_dict(input_df: pd.DataFrame, num_decimals: int) -> dict:
    """Convert dataframe to list of dictionaries with optional decimal rounding."""
    cols = input_df.columns
    column_groups = {
        "fossil": [c for c in cols if "fossil_" in str(c)],
        "biogenic": [c for c in cols if "biogenic_" in str(c)],
        "consumption": [c for c in cols if "consumption_" in str(c)],
        "export_of_oil_products": [c for c in cols if "export_of_oil_products_" in str(c)],
        "approximated": [c for c in cols if "approximated_" in str(c)],
        "trend": [
            c for c in cols
            if "trend_" in str(c) and "coefficient" not in str(c) and "slope" not in str(c)
        ],
    }

    rounded_df = input_df.round(num_decimals)

    return [
        series_to_dict(rounded_df.iloc[i], column_groups)
        for i in range(len(input_df))
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="National climate data calculations")
    parser.add_argument(
        "-o",
        "--outfile",
        default="output/national-data.json",
        type=str,
        help="Output filename (JSON formatted)",
    )
    parser.add_argument(
        "-n",
        "--num_decimals",
        default=2,
        type=int,
        help="Number of decimals to round to",
    )

    args = parser.parse_args()

    df = create_national_dataframe()

    temp = df_to_dict(df, args.num_decimals)

    output_file = args.outfile

    with open(output_file, "w", encoding="utf8") as json_file:
        # save dataframe as json file
        json.dump(temp, json_file, ensure_ascii=False, default=str)

    print("National data JSON file created and saved")
