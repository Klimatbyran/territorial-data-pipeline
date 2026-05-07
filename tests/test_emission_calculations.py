"""Test the emission calculations"""
# -*- coding: utf-8 -*-
import unittest
import datetime
import pandas as pd

from kpis.emissions.emission_data_calculations import (
    calculate_historical_change_percent,
    calculate_hit_net_zero,
    calculate_meets_paris_goal,
    emission_calculations,
)


LAST_YEAR_WITH_SMHI_DATA = 2021
CURRENT_YEAR = 2024


class TestEmissionCalculations(unittest.TestCase):
    """Test the emission calculations"""

    def test_calculate_historical_change_percent(self):
        """Test the historical change percent"""
        # Sample data frame for Östersund
        df_input = pd.DataFrame(
            {
                "Kommun": ["Östersund"],
                2015: [1],
                2020: [6],
                2021: [7],
            }
        )

        df_expected = df_input.copy()
        df_expected["historicalEmissionChangePercent"] = [38.31]

        df_result = calculate_historical_change_percent(
            df_input, "Kommun", LAST_YEAR_WITH_SMHI_DATA
        )

        pd.testing.assert_frame_equal(round(df_result, 2), round(df_expected, 2), check_exact=False)

    def test_does_meets_paris_goal(self):
        """Test the meets Paris goal"""
        df_input = pd.DataFrame(
            {
                "total_trend": [100],
                "totalCarbonLawPath": [110],
            }
        )

        df_expected = df_input.copy()
        df_expected["meetsParisGoal"] = [True]

        df_result = df_input.copy()
        df_result["meetsParisGoal"] = calculate_meets_paris_goal(
            df_input["total_trend"].iloc[0], df_input["totalCarbonLawPath"].iloc[0]
        )

        pd.testing.assert_frame_equal(df_result, df_expected)

    def test_calculate_hit_net_zero(self):
        """Test the hit net zero"""
        df_input = pd.DataFrame(
            {
                "Kommun": ["Ale", "Alingsås", "Gotland"],
                "approximated_2024": [1, 2, 15],
                "trend_emissions_slope": [1, -1, -5],
            }
        )

        df_expected = df_input.copy()
        df_expected["hit_net_zero"] = [None, datetime.date(2026, 1, 1), datetime.date(2027, 1, 1)]

        df_result = calculate_hit_net_zero(df_input, CURRENT_YEAR)

        pd.testing.assert_frame_equal(df_result, df_expected, check_exact=False)

    def test_does_not_meets_paris_goal(self):
        """Test the meets Paris goal"""
        df_input = pd.DataFrame(
            {
                "total_trend": [120],
                "totalCarbonLawPath": [110],
            }
        )

        df_expected = df_input.copy()
        df_expected["meetsParisGoal"] = [False]

        df_result = df_input.copy()
        df_result["meetsParisGoal"] = calculate_meets_paris_goal(
            df_input["total_trend"].iloc[0], df_input["totalCarbonLawPath"].iloc[0]
        )

        pd.testing.assert_frame_equal(df_result, df_expected)

    def test_does_exactly_meets_paris_goal(self):
        """Test the meets Paris goal"""
        df_input = pd.DataFrame(
            {
                "total_trend": [100],
                "totalCarbonLawPath": [100],
            }
        )

        df_expected = df_input.copy()
        df_expected["meetsParisGoal"] = [True]

        df_result = df_input.copy()
        df_result["meetsParisGoal"] = calculate_meets_paris_goal(
            df_input["total_trend"].iloc[0], df_input["totalCarbonLawPath"].iloc[0]
        )

        pd.testing.assert_frame_equal(df_result, df_expected)

    def test_emission_calculations_for_ale(self):
        """Test the emission calculations for Ale"""
        df_input = pd.DataFrame(
            {
                "Kommun": ["Ale"],
            }
        )

        df_expected = pd.DataFrame(
            {
                "Kommun": ["Ale"],
                1990: [128402.515874041],
                2000: [156477.764869377],
                2005: [146405.256919466],
                2010: [163665.861338809],
                2015: [158915.813495077],
                2020: [152008.05951377],
                2021: [158548.408843853],
                2022: [143277.933866814],
                2023: [136674.635738874],
                2024: [147637.709619733],
                "approximated_2024": [147637.70962],
                "approximated_2025": [146256.158823],
                "approximated_2026": [144874.608027],
                "trend_2026": [144874.608027],
                "trend_2027": [143493.057231],
                "trend_2028": [142111.506435],
                "trend_2029": [140729.955638],
                "trend_2030": [139348.404842],
                "trend_2031": [137966.854046],
                "trend_2032": [136585.30325],
                "trend_2033": [135203.752453],
                "trend_2034": [133822.201657],
                "trend_2035": [132440.650861],
                "trend_2036": [131059.100065],
                "trend_2037": [129677.549268],
                "trend_2038": [128295.998472],
                "trend_2039": [126914.447676],
                "trend_2040": [125532.89688],
                "trend_2041": [124151.346083],
                "trend_2042": [122769.795287],
                "trend_2043": [121388.244491],
                "trend_2044": [120006.693694],
                "trend_2045": [118625.142898],
                "trend_2046": [117243.592102],
                "trend_2047": [115862.041306],
                "trend_2048": [114480.490509],
                "trend_2049": [113098.939713],
                "trend_2050": [111717.388917],
                "trend_emissions_slope": [-1381.550796],
                "total_trend": [3207399.961802],
                "historicalEmissionChangePercent": [-0.814589],
                "hit_net_zero": [datetime.date(2130, 11, 12)],
                "totalCarbonLawPath": [1181351.373638],
                "meetsParisGoal": [False],
            }
        )

        df_result = round(emission_calculations(df_input), 6)

        pd.testing.assert_frame_equal(df_result, df_expected)

    def test_emission_calculations_for_aneby(self):
        """Test the emission calculations for Aneby"""
        df_input = pd.DataFrame(
            {
                "Kommun": ["Aneby"],
            }
        )

        df_expected = pd.DataFrame(
            {
                "Kommun": ["Aneby"],
                1990: [59917.9705772582],
                2000: [55050.5877253227],
                2005: [55467.1593075488],
                2010: [48948.2024317511],
                2015: [47972.4491322901],
                2020: [43136.9135443098],
                2021: [42537.8793419833],
                2022: [40886.5505772958],
                2023: [42039.3294612232],
                2024: [44925.090922263],
                "approximated_2024": [44925.090922263],
                "approximated_2025": [44019.32929115608],
                "approximated_2026": [43113.56766004916],
                "trend_2026": [43113.56766004916],
                "trend_2027": [42207.806028942236],
                "trend_2028": [41302.044397835314],
                "trend_2029": [40396.28276672839],
                "trend_2030": [39490.52113562147],
                "trend_2031": [38584.75950451455],
                "trend_2032": [37678.99787340763],
                "trend_2033": [36773.23624230071],
                "trend_2034": [35867.474611193786],
                "trend_2035": [34961.712980086864],
                "trend_2036": [34055.95134897994],
                "trend_2037": [33150.18971787302],
                "trend_2038": [32244.4280867661],
                "trend_2039": [31338.66645565918],
                "trend_2040": [30432.904824552257],
                "trend_2041": [29527.143193445336],
                "trend_2042": [28621.381562338414],
                "trend_2043": [27715.619931231493],
                "trend_2044": [26809.85830012457],
                "trend_2045": [25904.09666901765],
                "trend_2046": [24998.33503791073],
                "trend_2047": [24092.573406803807],
                "trend_2048": [23186.811775696886],
                "trend_2049": [22281.050144589964],
                "trend_2050": [21375.288513483043],
                "trend_emissions_slope": [-905.7616311069214],
                "total_trend": [806110.7021691524],
                "historicalEmissionChangePercent": [-0.7265744055952705],
                "hit_net_zero": [datetime.date(2073, 8, 7)],
                "totalCarbonLawPath": [351561.0711302647],
                "meetsParisGoal": [False],
            }
        )

        df_result = emission_calculations(df_input)

        pd.testing.assert_frame_equal(df_result, df_expected)


if __name__ == "__main__":
    unittest.main()
