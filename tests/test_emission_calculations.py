"""Test the emission calculations"""
# -*- coding: utf-8 -*-
import datetime
import unittest

import pandas as pd

from kpis.emissions.emission_data_calculations import (
    calculate_historical_change_percent,
    calculate_hit_net_zero,
    calculate_meets_paris_goal,
    emission_calculations,
)


LAST_YEAR_WITH_SMHI_DATA = 2021
CURRENT_YEAR = 2026
CURRENT_YEAR_HIT_NET_ZERO = 2024

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

        df_result = calculate_hit_net_zero(df_input, CURRENT_YEAR_HIT_NET_ZERO)

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
                1990: [128435.986125602],
                2000: [156510.786551878],
                2005: [146440.769045912],
                2010: [163714.141261533],
                2015: [158968.3923072],
                2020: [152060.795300923],
                2021: [158601.140801765],
                2022: [143330.665747717],
                2023: [136727.37178638],
                2024: [147474.355486],
                "approximated_2024": [147474.355486],
                "approximated_2025": [146092.836085],
                "approximated_2026": [144711.316683],
                "trend_2026": [144711.316683],
                "trend_2027": [143329.797282],
                "trend_2028": [141948.277881],
                "trend_2029": [140566.75848],
                "trend_2030": [139185.239078],
                "trend_2031": [137803.719677],
                "trend_2032": [136422.200276],
                "trend_2033": [135040.680875],
                "trend_2034": [133659.161473],
                "trend_2035": [132277.642072],
                "trend_2036": [130896.122671],
                "trend_2037": [129514.60327],
                "trend_2038": [128133.083868],
                "trend_2039": [126751.564467],
                "trend_2040": [125370.045066],
                "trend_2041": [123988.525665],
                "trend_2042": [122607.006263],
                "trend_2043": [121225.486862],
                "trend_2044": [119843.967461],
                "trend_2045": [118462.44806],
                "trend_2046": [117080.928658],
                "trend_2047": [115699.409257],
                "trend_2048": [114317.889856],
                "trend_2049": [112936.370455],
                "trend_2050": [111554.851053],
                "trend_emissions_slope": [-1381.519401],
                "total_trend": [3203327.096708],
                "historicalEmissionChangePercent": [-0.830434],
                "hit_net_zero": [datetime.date(2130, 9, 30)],
                "totalCarbonLawPath": [1180019.84663],
                "meetsParisGoal": [False],
            }
        )

        df_result = round(
            emission_calculations(df_input, current_year=CURRENT_YEAR), 6
        )

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
                1990: [59914.2330609742],
                2000: [55046.8988858276],
                2005: [55463.1947361921],
                2010: [48942.817642463],
                2015: [47966.5818395879],
                2020: [43131.0304818875],
                2021: [42531.9953237409],
                2022: [40880.6685106883],
                2023: [42033.4493728939],
                2024: [44919.2078539399],
                "approximated_2024": [44919.2078539399],
                "approximated_2025": [44013.44343524281],
                "approximated_2026": [43107.67901654571],
                "trend_2026": [43107.67901654571],
                "trend_2027": [42201.91459784862],
                "trend_2028": [41296.150179151526],
                "trend_2029": [40390.38576045443],
                "trend_2030": [39484.62134175734],
                "trend_2031": [38578.856923060244],
                "trend_2032": [37673.09250436315],
                "trend_2033": [36767.32808566606],
                "trend_2034": [35861.56366696896],
                "trend_2035": [34955.79924827187],
                "trend_2036": [34050.034829574775],
                "trend_2037": [33144.27041087768],
                "trend_2038": [32238.505992180588],
                "trend_2039": [31332.741573483494],
                "trend_2040": [30426.9771547864],
                "trend_2041": [29521.212736089306],
                "trend_2042": [28615.448317392213],
                "trend_2043": [27709.68389869512],
                "trend_2044": [26803.919479998025],
                "trend_2045": [25898.15506130093],
                "trend_2046": [24992.390642603837],
                "trend_2047": [24086.626223906744],
                "trend_2048": [23180.86180520965],
                "trend_2049": [22275.097386512556],
                "trend_2050": [21369.332967815462],
                "trend_emissions_slope": [-905.7644186970938],
                "total_trend": [805962.6498045147],
                "historicalEmissionChangePercent": [-0.7266698014856132],
                "hit_net_zero": [datetime.date(2073, 8, 5)],
                "totalCarbonLawPath": [351513.05335001746],
                "meetsParisGoal": [False],
            }
        )

        df_result = emission_calculations(df_input, current_year=CURRENT_YEAR)

        pd.testing.assert_frame_equal(df_result, df_expected)


if __name__ == "__main__":
    unittest.main()
