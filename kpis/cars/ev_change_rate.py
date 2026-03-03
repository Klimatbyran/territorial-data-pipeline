# pylint: disable=invalid-name
import pandas as pd
from scipy.stats import linregress


# calculations based on trafa data
PATH_CARS_DATA_2015_TO_2024 = "kpis/cars/sources/kpi1_calculations.xlsx"
# path to data from 2025 onwards
PATH_CARS_DATA_2025 = "kpis/cars/sources/fordon-i-lan-och-kommuner-2025.xlsx"


def get_ev_share_2015_to_2024(territory_name: str, to_percent: bool = True):
    """Get share of newly registered rechargeable cars per territory and year 2015-2024.
    This is an old data source, that we used before moving all calculations to this file."""
    df_raw_cars = pd.read_excel(PATH_CARS_DATA_2015_TO_2024)

    df_raw_cars.columns = df_raw_cars.iloc[1]  # name columns after row
    df_raw_cars = df_raw_cars.drop([0, 1])  # drop usless rows
    df_raw_cars = df_raw_cars.reset_index(drop=True)

    years = range(2015, 2024+1)

    for year in years:
        df_raw_cars[f"evChange_{year}"] = df_raw_cars[year] * (100 if to_percent else 1)

    yearly_columns = [f"evChange_{year}" for year in years]
    df_cars = df_raw_cars.filter([territory_name] + yearly_columns, axis=1)
    return df_cars

def get_ev_share_from_2025(territory_name: str, to_percent: bool = True):
    """Get share of newly registered rechargeable cars per territory and year from 
    2025 onwards. Calculates total number of new elbilar (electric cars) + laddhybrider
    (plug-in hybrids) and their share of total number of new cars."""
    # Read Tabell 5 Personbil which contains new registrations by territory and fuel type
    df_raw_cars = pd.read_excel(PATH_CARS_DATA_2025, sheet_name='Tabell 5 Personbil', header=None)

    df_raw_cars.columns = df_raw_cars.iloc[3]  # set column names from row 3 (Swedish headers)
    df_raw_cars = df_raw_cars.drop(range(7))  # drop header rows
    df_raw_cars = df_raw_cars.reset_index(drop=True)

    # Convert relevant columns to numeric, handling '–' as NaN
    df_raw_cars['El'] = pd.to_numeric(df_raw_cars['El'], errors='coerce')
    df_raw_cars['Laddhybrider'] = pd.to_numeric(df_raw_cars['Laddhybrider'], errors='coerce')
    df_raw_cars['Totalt'] = pd.to_numeric(df_raw_cars['Totalt'], errors='coerce')

    df_raw_cars['totalRechargeable'] = df_raw_cars['El'] + df_raw_cars['Laddhybrider']

    # Calculate share of rechargeable cars for 2025
    df_raw_cars['evChange_2025'] = (
        df_raw_cars['totalRechargeable'] / df_raw_cars['Totalt']
        ) * 100 if to_percent else 1

    df_cars = df_raw_cars[[territory_name, 'evChange_2025']].copy()
    df_cars[territory_name] = df_cars[territory_name].str.strip()  # remove trailing spaces

    return df_cars

def get_ev_change_rate_per_territory(row: pd.Series):
    """Calculate evChangeRate for a single territory row using linear regression 
    of all evChange_ columns."""

    ev_change_cols = [col for col in row.index if col.startswith('evChange_')]

    years = []
    values = []

    for col in sorted(ev_change_cols):
        year = int(col.split('_')[1])
        years.append(year)

        value = float(row[col][0])
        values.append(value)

    slope, _intercept, _r_value, _p_value, _std_err = linregress(years, values)
    slope_to_integer = slope * 1

    return slope_to_integer

def get_ev_change_rate(df_input: pd.DataFrame, territory_name: str, to_percent: bool = True):
    """Calculate the change rate of newly registered rechargeable cars per territory and year."""

    df_cars_to_2024 = get_ev_share_2015_to_2024(territory_name, to_percent)
    df_cars_from_2025 = get_ev_share_from_2025(territory_name, to_percent)

    df_cars = df_cars_to_2024.merge(df_cars_from_2025, on=territory_name, how="left")
    df_cars['evChangeRate'] = None

    for idx, row in df_cars.iterrows():
        df_cars.at[idx, 'evChangeRate'] = get_ev_change_rate_per_territory(row)

    df_result = df_input.merge(df_cars, on=territory_name, how="left")

    return df_result
