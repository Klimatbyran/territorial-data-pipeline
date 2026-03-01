# pylint: disable=invalid-name
import pandas as pd


# calculations based on trafa data
PATH_CARS_DATA = "kpis/cars/sources/kpi1_calculations.xlsx"


def get_ev_change_rate_2015_to_2024(to_percent: bool = True):
    """Get change rate of newly registered rechargeable cars per municipality and year 2015-2024.
    This is an old data source, that we used before we had all calculations in this file."""
    df_raw_cars = pd.read_excel(PATH_CARS_DATA)

    df_raw_cars.columns = df_raw_cars.iloc[1]  # name columns after row
    df_raw_cars = df_raw_cars.drop([0, 1])  # drop usless rows
    df_raw_cars = df_raw_cars.reset_index(drop=True)

    years = [
        2015,
        2016,
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
    ]

    for year in years:
        df_raw_cars[f"evChange_{year}"] = df_raw_cars[year] * (100 if to_percent else 1)

    df_raw_cars["evChangeRate"] = pd.to_numeric(df_raw_cars["evChangeRate"], errors='coerce') * (
        100 if to_percent else 1
    )

    yearly_columns = [f"evChange_{year}" for year in years]
    df_cars = df_raw_cars.filter(["Kommun", "evChangeRate"] + yearly_columns, axis=1)
    return df_cars

def get_ev_change_rate(df, to_percent: bool = True):
    """Calculate the change rate of newly registered rechargeable cars per municipality and year."""

    df_cars = get_ev_change_rate_2015_to_2024(to_percent)
    df = df.merge(df_cars, on="Kommun", how="left")

    return df
