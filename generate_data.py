# -*- coding: utf-8 -*-
"""Generate territorial climate data JSON for municipalities, regions, and national level."""

import argparse
import json
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd

from facts.coatOfArms.coat_of_arms import (
    get_coat_of_arms,
    get_coat_of_arms_from_csv,
    get_region_coat_of_arms_from_csv,
)
from facts.municipalities_counties import get_municipalities
from facts.political.political_rule import get_political_rule_municipalities
from kpis.bicycles.bicycle_data_calculations import calculate_bike_lane_per_capita
from kpis.cars.electric_vehicle_per_charge_points import (
    get_electric_vehicle_per_charge_points,
)
from kpis.cars.ev_change_rate import get_ev_change_rate
from kpis.consumption.consumption_emissions import (
    get_consumption_emissions,
    get_regional_consumption_emissions,
)
from kpis.emissions.emission_data_calculations import emission_calculations
from kpis.emissions.regional_emissions import regional_emission_calculations
from kpis.emissions.swedish_emissions import create_swedish_emissions_df
from kpis.plans.plans_data_prep import get_climate_plans
from kpis.procurements.climate_requirements_in_procurements import get_procurement_data
from sector_emissions import generate_sector_emissions, parse_selected_levels

# Notebook from ClimateView that our calculations are based on:
# https://colab.research.google.com/drive/1qqMbdBTu5ulAPUe-0CRBmFuh8aNOiHEb?usp=sharing


def _extract_territorial_emission_columns(
    input_df: pd.DataFrame,
) -> Tuple[List[Any], List[Any], List[Any]]:
    """Extract column groups used by regional and municipality output."""
    historical_columns = [col for col in input_df.columns if str(col).isdigit()]
    approximated_columns = [
        col for col in input_df.columns if "approximated_" in str(col)
    ]
    trend_columns = [
        col
        for col in input_df.columns
        if "trend_" in str(col) and "coefficient" not in str(col) and "slope" not in str(col)
    ]
    return historical_columns, approximated_columns, trend_columns


def territorial_df_to_dict(
    input_df: pd.DataFrame,
    num_decimals: int,
    series_to_dict: Callable[..., Dict],
) -> List[Dict]:
    """Convert a territorial dataframe to a list of dictionaries."""
    historical_columns, approximated_columns, trend_columns = (
        _extract_territorial_emission_columns(input_df)
    )
    rounded_df = input_df.round(num_decimals)

    return [
        series_to_dict(
            rounded_df.iloc[i],
            historical_columns,
            approximated_columns,
            trend_columns,
        )
        for i in range(len(input_df))
    ]


def save_json(data: List[Dict], output_file: str) -> None:
    """Write data to a JSON file."""
    with open(output_file, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, default=str)


def format_region_name(value: Any) -> Any:
    """Format the region name to match the standard format (capitalize first letter, lowercase rest)."""
    if not isinstance(value, str):
        return value
    name = value.strip().lower()
    if name.endswith(" län"):
        base = name[:-4]
        return f"{base.title()} län"
    return name.title()


def create_municipality_dataframe(to_percentage: bool) -> pd.DataFrame:
    """Create a comprehensive climate dataframe by merging multiple data sources."""
    municipalities_df = get_municipalities()
    print("1. Municipalities loaded and prepped")

    emissions_df = emission_calculations(municipalities_df)
    print("2. Climate data and calculations added")

    ev_change_rate_df = get_ev_change_rate("Kommun", to_percentage)
    emissions_with_ev_change_rate_df = emissions_df.merge(
        ev_change_rate_df, on="Kommun", how="left"
    )
    print("3. Hybrid car data and calculations added")

    climate_plans_df = get_climate_plans(emissions_with_ev_change_rate_df)
    print("4. Climate plans added")

    bike_lane_df = calculate_bike_lane_per_capita()
    climate_plans_with_bike_df = climate_plans_df.merge(
        bike_lane_df, on="Kommun", how="left"
    )
    print("5. Bicycle data added")

    consumption_emissions_df = get_consumption_emissions()
    bike_lane_with_consumption_emissions_df = consumption_emissions_df.merge(
        climate_plans_with_bike_df, on="Kommun", how="left"
    )
    print("6. Consumption emission data added")

    evcp_source_path = "kpis/cars/sources/powercircle_municipality_data_dec_2025.csv"
    evpc_df = get_electric_vehicle_per_charge_points("Kommun", evcp_source_path)
    evpc_df["Kommun"] = evpc_df["Kommun"].str.strip().str.title()
    consumption_emissions_with_evpc_df = bike_lane_with_consumption_emissions_df.merge(
        evpc_df, on="Kommun", how="left"
    )
    print("7. CPEV for December 2023 added")

    procurement_df = get_procurement_data()
    result_df = consumption_emissions_with_evpc_df.merge(
        procurement_df, on="Kommun", how="left"
    )
    print("8. Climate requirements in procurements added")

    political_rule_df = get_political_rule_municipalities()
    result_df = result_df.merge(political_rule_df, on="Kommun", how="left")
    print("9. Political rule added")

    result_df["coatOfArms"] = result_df["Kommun"].apply(get_coat_of_arms_from_csv)
    print("10. Coat of arms added")

    return result_df.sort_values(by="Kommun").reset_index(drop=True)


def municipality_series_to_dict(
    row: pd.Series,
    historical_columns: List[Any],
    approximated_columns: List[Any],
    trend_columns: List[Any],
) -> Dict:
    """Transform a municipality row into the output dictionary format."""
    return {
        "name": row["Kommun"],
        "logoUrl": row["coatOfArms"],
        "region": row["Län"],
        "emissions": {str(year): row[year] for year in historical_columns},
        "totalTrend": row["total_trend"],
        "totalCarbonLaw": row["totalCarbonLawPath"],
        "approximatedHistoricalEmission": {
            year.replace("approximated_", ""): row[year]
            for year in approximated_columns
        },
        "trend": {year.replace("trend_", ""): row[year] for year in trend_columns},
        "emissionsSlope": row["trend_emissions_slope"],
        "historicalEmissionChangePercent": row["historicalEmissionChangePercent"],
        "hitNetZero": row["hit_net_zero"],
        "electricCarChangePercent": row["evChangeRate"],
        "climatePlanLink": row["Länk till aktuell klimatplan"],
        "climatePlanYear": row["Antagen år"],
        "climatePlanComment": row["Namn, giltighetsår, kommentar"],
        "bicycleMetrePerCapita": row["bike_metre_per_capita"],
        "totalConsumptionEmission": row["consumption_emissions"],
        "electricVehiclePerChargePoints": (
            row["EVPC"] if pd.notna(row["EVPC"]) else None
        ),
        "procurementScore": int(row["procurementScore"]),
        "procurementLink": row["procurementLink"],
        "politicalRule": row["Rule"],
        "politicalKSO": row["KSO"],
    }


def create_regional_dataframe() -> pd.DataFrame:
    """Create a comprehensive climate dataframe by merging multiple data sources."""
    regions_df = regional_emission_calculations()
    print("1. Regional climate data and calculations added")

    evcp_source_path = "kpis/cars/sources/powercircle_region_data_dec_2025.csv"
    evpc_df = get_electric_vehicle_per_charge_points("Län", evcp_source_path)
    evpc_df["Län"] = evpc_df["Län"].apply(format_region_name)
    regions_df = regions_df.merge(evpc_df, on="Län", how="left")
    print("2. CPEV for December 2023 added")

    consumption_df = get_regional_consumption_emissions()
    regions_df = regions_df.merge(consumption_df, on="Län", how="left")
    print("3. Consumption emission data added")

    regions_df["coatOfArms"] = regions_df["Län"].apply(get_region_coat_of_arms_from_csv)
    print("4. Coat of arms added")

    return regions_df


def regional_series_to_dict(
    row: pd.Series,
    historical_columns: List[Any],
    approximated_columns: List[Any],
    trend_columns: List[Any],
) -> Dict:
    """Transform a regional row into the output dictionary format."""
    return {
        "region": row["Län"],
        "logoUrl": row["coatOfArms"],
        "emissions": {str(year): row[year] for year in historical_columns},
        "totalTrend": row["total_trend"],
        "totalCarbonLaw": row["totalCarbonLawPath"],
        "approximatedHistoricalEmission": {
            year.replace("approximated_", ""): row[year]
            for year in approximated_columns
        },
        "trend": {year.replace("trend_", ""): row[year] for year in trend_columns},
        "emissionsSlope": row["trend_emissions_slope"],
        "historicalEmissionChangePercent": row["historicalEmissionChangePercent"],
        "meetsParis": row["total_trend"] / row["totalCarbonLawPath"] < 1,
        "municipalities": row["municipalities"],
        "electricVehiclePerChargePoints": (
            row["EVPC"] if pd.notna(row["EVPC"]) else None
        ),
        "totalConsumptionEmission": row["consumption_emissions"],
    }


def create_national_dataframe() -> pd.DataFrame:
    """Create a comprehensive national climate dataframe by merging multiple data sources."""
    national_df = create_swedish_emissions_df()
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


def national_series_to_dict(row: pd.Series, column_groups: Dict[str, List[Any]]) -> Dict:
    """Transform a national row into the output dictionary format."""
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
        "eCommerceEmissions": {
            str(year.strip("e_commerce_")): row[year]
            for year in column_groups["e_commerce"]
        },
    }


def national_df_to_dict(input_df: pd.DataFrame, num_decimals: int) -> List[Dict]:
    """Convert national dataframe to list of dictionaries with optional decimal rounding."""
    cols = input_df.columns
    column_groups = {
        "fossil": [c for c in cols if "fossil_" in str(c) and "approximated_fossil_" not in str(c)],
        "biogenic": [
            c for c in cols
            if "biogenic_" in str(c) and "approximated_biogenic_" not in str(c)
        ],
        "consumption": [
            c for c in cols
            if "consumption_" in str(c) and "approximated_consumption_" not in str(c)
        ],
        "export_of_oil_products": [
            c for c in cols
            if "export_of_oil_products_" in str(c)
            and "approximated_export_of_oil_products_" not in str(c)
        ],
        "e_commerce": [
            c for c in cols
            if str(c).startswith("e_commerce_")
        ],
    }

    rounded_df = input_df.round(num_decimals)

    return [
        national_series_to_dict(rounded_df.iloc[i], column_groups)
        for i in range(len(input_df))
    ]


def generate_municipality_data(
    output_file: str,
    num_decimals: int,
    to_percentage: bool,
) -> None:
    """Generate municipality climate data JSON."""
    df = create_municipality_dataframe(to_percentage)
    data = territorial_df_to_dict(df, num_decimals, municipality_series_to_dict)
    save_json(data, output_file)
    print("Climate data JSON file created and saved")


def generate_regional_data(output_file: str, num_decimals: int) -> None:
    """Generate regional climate data JSON."""
    df = create_regional_dataframe()
    data = territorial_df_to_dict(df, num_decimals, regional_series_to_dict)
    save_json(data, output_file)
    print("Regional data JSON file created and saved")


def generate_national_data(output_file: str, num_decimals: int) -> None:
    """Generate national climate data JSON."""
    df = create_national_dataframe()
    data = national_df_to_dict(df, num_decimals)
    save_json(data, output_file)
    print("National data JSON file created and saved")


def df_to_dict(input_df: pd.DataFrame, num_decimals: int) -> List[Dict]:
    """Convert a regional dataframe to JSON-ready dictionaries (backward-compatible alias)."""
    return territorial_df_to_dict(input_df, num_decimals, regional_series_to_dict)


TERRITORIAL_DATA_CONFIG = {
    "municipalities": {
        "label": "Municipality data",
        "output_file": "output/municipality-data.json",
        "default_decimals": 3,
    },
    "regions": {
        "label": "Regional data",
        "output_file": "output/regional-data.json",
        "default_decimals": 2,
    },
    "national": {
        "label": "National data",
        "output_file": "output/national-data.json",
        "default_decimals": 2,
    },
}


def generate_territorial_data_for_level(
    level: str,
    num_decimals: int,
    to_percentage: bool,
    output_file: str | None = None,
) -> None:
    """Generate territorial climate data JSON for a single level."""
    config = TERRITORIAL_DATA_CONFIG[level]
    output_path = output_file or config["output_file"]

    if level == "municipalities":
        generate_municipality_data(output_path, num_decimals, to_percentage)
    elif level == "regions":
        generate_regional_data(output_path, num_decimals)
    else:
        generate_national_data(output_path, num_decimals)


def generate_all_data(
    levels: List[str],
    num_decimals: int | None,
    to_percentage: bool,
    output_files: Dict[str, str] | None = None,
) -> None:
    """Generate territorial and sector emissions data for selected levels."""
    output_files = output_files or {}

    for level in levels:
        config = TERRITORIAL_DATA_CONFIG[level]
        print(f"\n=== {config['label']} ===")
        level_decimals = (
            num_decimals if num_decimals is not None else config["default_decimals"]
        )
        generate_territorial_data_for_level(
            level,
            level_decimals,
            to_percentage,
            output_file=output_files.get(level),
        )

    generate_sector_emissions(
        levels=levels,
        num_decimals=num_decimals if num_decimals is not None else 2,
    )

    if len(levels) == len(TERRITORIAL_DATA_CONFIG):
        print("\nAll data files updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate territorial climate and sector emissions data"
    )
    parser.add_argument(
        "--municipalities",
        action="store_true",
        help="Generate municipality data only",
    )
    parser.add_argument(
        "--regions",
        action="store_true",
        help="Generate regional data only",
    )
    parser.add_argument(
        "--national",
        action="store_true",
        help="Generate national data only",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="Output filename (JSON formatted; only valid with a single level flag)",
    )
    parser.add_argument(
        "-t",
        "--to_percentage",
        action="store_true",
        default=True,
        help="Convert to percentages (municipality data only)",
    )
    parser.add_argument(
        "-n",
        "--num_decimals",
        type=int,
        help="Number of decimals to round to",
    )

    args = parser.parse_args()
    selected_levels = parse_selected_levels(args)

    if args.outfile and len(selected_levels) != 1:
        parser.error("--outfile can only be used with a single level flag")

    output_files = {selected_levels[0]: args.outfile} if args.outfile else {}

    generate_all_data(
        levels=selected_levels,
        num_decimals=args.num_decimals,
        to_percentage=args.to_percentage,
        output_files=output_files,
    )
