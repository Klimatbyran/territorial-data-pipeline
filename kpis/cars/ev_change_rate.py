# pylint: disable=invalid-name
import pandas as pd


# calculations based on trafa data
PATH_CARS_DATA_2015_TO_2024 = "kpis/cars/sources/kpi1_calculations.xlsx"
PATH_CARS_DATA_2025 = "kpis/cars/sources/fordon-i-lan-och-kommuner-2025.xlsx"


def get_ev_change_rate_2015_to_2024(to_percent: bool = True):
    """Get change rate of newly registered rechargeable cars per municipality and year 2015-2024.
    This is an old data source, that we used before we had all calculations in this file."""
    df_raw_cars = pd.read_excel(PATH_CARS_DATA_2015_TO_2024)

    df_raw_cars.columns = df_raw_cars.iloc[1]  # name columns after row
    df_raw_cars = df_raw_cars.drop([0, 1])  # drop usless rows
    df_raw_cars = df_raw_cars.reset_index(drop=True)

    years = range(2015, 2024+1)

    for year in years:
        df_raw_cars[f"evChange_{year}"] = df_raw_cars[year] * (100 if to_percent else 1)

    df_raw_cars["evChangeRate"] = pd.to_numeric(df_raw_cars["evChangeRate"], errors='coerce') * (
        100 if to_percent else 1
    )

    yearly_columns = [f"evChange_{year}" for year in years]
    df_cars = df_raw_cars.filter(["Kommun", "evChangeRate"] + yearly_columns, axis=1)
    return df_cars

def get_ev_change_rate_from_2025(to_percent: bool = True):
    """Get change rate of newly registered rechargeable cars per municipality and year from 
    2025 onwards. Calculates total number of new elbilar (electric cars) + laddhybrider
    (plug-in hybrids) and their share of total number of new cars."""
    # Read Tabell 5 Personbil which contains new registrations by municipality and fuel type
    df_raw_cars = pd.read_excel(PATH_CARS_DATA_2025, sheet_name='Tabell 5 Personbil', header=None)

    # Set column names from row 3 (Swedish headers)
    df_raw_cars.columns = df_raw_cars.iloc[3]
    # Drop header rows (0-6) and reset index
    df_raw_cars = df_raw_cars.drop(range(7))
    df_raw_cars = df_raw_cars.reset_index(drop=True)

    # Convert relevant columns to numeric, handling '–' as NaN
    df_raw_cars['El'] = pd.to_numeric(df_raw_cars['El'], errors='coerce')
    df_raw_cars['Laddhybrider'] = pd.to_numeric(df_raw_cars['Laddhybrider'], errors='coerce')
    df_raw_cars['Totalt'] = pd.to_numeric(df_raw_cars['Totalt'], errors='coerce')

    # Calculate total rechargeable cars (El + Laddhybrider)
    df_raw_cars['totalRechargeable'] = df_raw_cars['El'] + df_raw_cars['Laddhybrider']

    # Calculate share of rechargeable cars
    df_raw_cars['rechargeableShare'] = (
        df_raw_cars['totalRechargeable'] / df_raw_cars['Totalt']
        ) * 100 if to_percent else 1

    # Select and rename columns for output
    df_cars = df_raw_cars[['Kommun', 'totalRechargeable', 'rechargeableShare']].copy()
    df_cars.columns = ['Kommun', 'totalRechargeable', 'rechargeableShare']

    # Clean up Kommun names (remove trailing spaces)
    df_cars['Kommun'] = df_cars['Kommun'].str.strip()

    return df_cars

def get_ev_change_rate(df, to_percent: bool = True):
    """Calculate the change rate of newly registered rechargeable cars per municipality and year."""

    df_cars = get_ev_change_rate_2015_to_2024(to_percent)
    df = df.merge(df_cars, on="Kommun", how="left")

    return df
