# pylint: disable=invalid-name
# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

from kpis.emissions.historical_data_calculations import get_n_prep_data_from_smhi
from kpis.emissions.trend_calculations import calculate_trend, calculate_total_trend
from kpis.emissions.carbon_law_calculations import calculate_carbon_law_total


CURRENT_YEAR = datetime.now().year  # current year
YEAR_SECONDS = 60 * 60 * 24 * 365   # a year in seconds
LAST_YEAR_WITH_SMHI_DATA = 2024  # last year for which the National Emission database has data
END_YEAR = 2050

CARBON_LAW_REDUCTION_RATE = 0.1172

PATH_SMHI = (
    "https://nationellaemissionsdatabasen.smhi.se/api/"
    + "getexcelfile/?county=0&municipality=0&sub=GGT"
)


def calculate_historical_change_percent(df, column_name, last_year_in_range):
    """
    Calculate historical emission change as compund annual growth rate (CAGR) from 2015 through
    the last available SMHI year.

    Uses SMHI year columns: 2015 and 2020 through ``last_year_in_range`` (annual from 2020).
    The CAGR is computed from the 2015 value to the value for ``last_year_in_range`` over the
    full calendar span, so missing intermediate years are summarised as one constant annual rate.

    Args:
        df (pandas.DataFrame): The input DataFrame containing emission data.
        column_name (string): name of column to sort on
        last_year_in_range (int): last year with data

    Returns:
        pandas.DataFrame: The input DataFrame with an column
                          'historicalEmissionChangePercent' representing
                          the CAGR in percent for each row.
    """

    years = [2015] + list(range(2020, last_year_in_range + 1))

    temp = []
    df = df.sort_values(column_name, ascending=True)
    first_year = years[0]
    last_year = years[-1]
    year_span = last_year - first_year

    for row_idx in range(len(df)):
        emissions = np.array(df.iloc[row_idx][years], dtype=float)
        start_e = float(emissions[0])
        end_e = float(emissions[-1])

        cagr_fraction = (end_e / start_e) ** (1.0 / year_span) - 1.0
        temp.append(float(100.0 * cagr_fraction))

    df["historicalEmissionChangePercent"] = temp

    return df

def calculate_hit_net_zero(input_df, current_year):
    """
    Calculates the date and year for when each municipality hits net zero emissions (if so).
    This is done by deriving where the linear trend line crosses the time axis.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the emissions data.
        current_year (int): Current year

    Returns:
        pandas.DataFrame: The input DataFrame with an additional column 'hit_net_zero' that contains
        the date when net zero emissions are reached for each municipality.
    """
    dates = []
    for i in range(len(input_df)):
        slope = input_df.iloc[i]["trend_emissions_slope"]

        col_name = (
            current_year
            if current_year in input_df.columns
            else f"approximated_{current_year}"
        )
        emissions_value_raw = input_df.iloc[i][col_name]
        emissions_value = float(emissions_value_raw)

        if slope < 0:
            # E(t) = E0 + slope*(t - y0) => t_cross = y0 - E0/slope
            y0 = int(current_year)
            t_cross = y0 - (emissions_value / slope)

            whole_year = int(t_cross)
            frac = t_cross - whole_year
            base_dt = datetime(whole_year, 1, 1)
            date_cross = (base_dt + relativedelta(seconds=int(frac * YEAR_SECONDS))).date()
            dates.append(date_cross)
        else:
            dates.append(None)

    df_out = input_df.copy()
    df_out["hit_net_zero"] = dates
    return df_out


def calculate_meets_paris_goal(total_trend, total_carbon_law_path):
    """
    Calculate if the municipality meets the Paris goal.
    """
    return total_trend <= total_carbon_law_path


def emission_calculations(df, current_year=None):
    """
    Perform emission calculations based on the given dataframe.

    Parameters:
    - df (pandas.DataFrame): The input dataframe containing municipality data.
    - current_year (int, optional): Year to use for projections. Defaults to the current year.

    Returns:
    - (pandas.DataFrame): The resulting dataframe with emissions data.
    """
    if current_year is None:
        current_year = CURRENT_YEAR

    df_smhi = get_n_prep_data_from_smhi(df)

    df_trend_and_approximated = calculate_trend(df_smhi, current_year, END_YEAR)

    df_trend_and_approximated["total_trend"] = calculate_total_trend(df_trend_and_approximated)

    df_historical_change_percent = calculate_historical_change_percent(
        df_trend_and_approximated, "Kommun", LAST_YEAR_WITH_SMHI_DATA
    )

    df_hit_net_zero = calculate_hit_net_zero(df_historical_change_percent, LAST_YEAR_WITH_SMHI_DATA)

    df_carbon_law = calculate_carbon_law_total(
        df_hit_net_zero,
        current_year,
        END_YEAR,
        CARBON_LAW_REDUCTION_RATE,
    )

    df_carbon_law["meetsParisGoal"] = df_carbon_law.apply(
        lambda row: calculate_meets_paris_goal(
            row["total_trend"], row["totalCarbonLawPath"]
        ),
        axis=1,
    )

    return df_carbon_law
