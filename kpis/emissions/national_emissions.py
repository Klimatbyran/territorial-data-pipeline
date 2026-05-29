# pylint: disable=invalid-name
# -*- coding: utf-8 -*-

from kpis.emissions.historical_data_calculations import get_n_prep_national_data_from_smhi


def national_emission_calculations():
    """
    Perform emission calculations for national level.

    Parameters:
    Returns:
    - (pandas.DataFrame): The resulting dataframe with emissions data.
    """
    return get_n_prep_national_data_from_smhi()
