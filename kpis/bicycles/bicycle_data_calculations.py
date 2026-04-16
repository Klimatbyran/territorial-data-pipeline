"""Bicycle KPI calculations."""

import pandas as pd


PATH_BICYCLE_DATA = (
    "kpis/bicycles/sources/antal-meter-cykelnat-per-vaghallare-efter-lan-och-kommun.xlsx"
)
SHEET_NAME_BICYCLES = "2025"
PATH_POPULATION_DATA = "kpis/bicycles/sources/000007SF_20260416-131411.xlsx"


def calculate_bike_lane_per_capita():
    """
    Perform calculations on bicycle data and population data on municipality level.

    This function reads bicycle data and population data from Excel files, performs
    data cleaning and merging, and calculates the bike lane per capita per municipality.

    Returns:
        pandas.DataFrame: A DataFrame containing the calculated bike lane per capita.
    """

    raw_bicycle_df = pd.read_excel(PATH_BICYCLE_DATA, sheet_name=SHEET_NAME_BICYCLES)
    bicycle_length_columns = ["Enskild", "Kommunal", "Statlig"]
    raw_bicycle_df[bicycle_length_columns] = (
        raw_bicycle_df[bicycle_length_columns]
        .where(raw_bicycle_df[bicycle_length_columns] != "-", 0)
        .apply(pd.to_numeric)
        .astype(int)
    )
    raw_bicycle_df["Totalsumma"] = (
        raw_bicycle_df["Enskild"] + raw_bicycle_df["Kommunal"] + raw_bicycle_df["Statlig"]
    )

    bicycle_df = raw_bicycle_df[["Kommun", "Totalsumma"]]

    # Clean bicycle dataframe
    cleaned_bicycle_df = bicycle_df.loc[2:].copy()  # Drop last rows
    cleaned_bicycle_df.loc[cleaned_bicycle_df["Kommun"] == "Malung", "Kommun"] = "Malung-Sälen"
    cleaned_bicycle_df.loc[cleaned_bicycle_df["Kommun"] == "Upplands-Väsby", "Kommun"] = (
        "Upplands Väsby"
    )

    raw_population_df = pd.read_excel(PATH_POPULATION_DATA, skiprows=2)
    raw_population_df = raw_population_df.rename(
        columns={"Unnamed: 0": "Kommun", "2025M12": "Folkmängd"}
    )

    population_df = raw_population_df.loc[:289].copy()  # Drop last rows
    population_df["Kommun"] = (
        population_df["Kommun"].astype(str).str.replace(r"^.{4}\s", "", regex=True)
    )

    # Merge bicycle and population dataframes
    merged_df = cleaned_bicycle_df.merge(population_df, on="Kommun", how="left")

    # Calculate bike lane per capita
    merged_df["bike_metre_per_capita"] = merged_df["Totalsumma"] / merged_df["Folkmängd"]
    result_df = (
        merged_df[["Kommun", "bike_metre_per_capita"]]
        .sort_values(by="Kommun")
        .reset_index(drop=True)
    )
    
    print(result_df.head())

    return result_df
