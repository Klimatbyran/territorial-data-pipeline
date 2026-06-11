# pylint: disable=invalid-name
# -*- coding: utf-8 -*-

from datetime import datetime

from kpis.emissions.historical_data_calculations import get_n_prep_regional_data_from_smhi
from kpis.emissions.trend_calculations import calculate_trend, calculate_total_trend
from kpis.emissions.carbon_law_calculations import calculate_carbon_law_total
from kpis.emissions.emission_data_calculations import (
    calculate_historical_change_percent,
    calculate_meets_paris_goal,
)
from kpis.emissions.emission_data_calculations import LAST_YEAR_WITH_SMHI_DATA


CURRENT_YEAR = datetime.now().year  # current year
END_YEAR = 2050

CARBON_LAW_REDUCTION_RATE = 0.1172

PATH_SMHI = (
    "https://nationellaemissionsdatabasen.smhi.se/api/"
    + "getexcelfile/?county=0&municipality=0&sub=GGT"
)

def regional_emission_calculations():
    """
    Perform emission calculations for regions.

    Parameters:
    Returns:
    - (pandas.DataFrame): The resulting dataframe with emissions data.
    """

    total_emissions_df = get_n_prep_regional_data_from_smhi()

    df_trend_and_approximated = calculate_trend(total_emissions_df, CURRENT_YEAR, END_YEAR)

    df_trend_and_approximated["total_trend"] = calculate_total_trend(
        df_trend_and_approximated
    )

    df_historical_change_percent = calculate_historical_change_percent(
        df_trend_and_approximated, "Län", LAST_YEAR_WITH_SMHI_DATA
    )

    df_carbon_law = calculate_carbon_law_total(
        df_historical_change_percent,
        CURRENT_YEAR,
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
