# -*- coding: utf-8 -*-
import unittest
import numpy as np
import pandas as pd

from kpis.cars.ev_change_rate import (
    get_ev_change_rate,
    get_ev_share_2015_to_2024,
    get_ev_share_from_2025,
    get_ev_change_rate_per_territory,
)

ale_input = {
    "Kommun": ["Ale"],
    "evChange_2015": [2.64385692068429],
    "evChange_2016": [1.28865979381443],
    "evChange_2017": [1.64383561643836],
    "evChange_2018": [5.02873563218391],
    "evChange_2019": [7.08860759493671],
    "evChange_2020": [27.338129496402903],
    "evChange_2021": [41.7276720351391],
    "evChange_2022": [55.6171983356449],
    "evChange_2023": [54.9056603773585],
    "evChange_2024": [48.8612836438923],
}

ALE_EV_SHARE_2025 = 59.95575221

ale_expected = {
    "Kommun": ["Ale"],
    "evChangeRate": [7.0222857817156505],
}

class TestBicycleCalculations(unittest.TestCase):
    """Test the ev change rate calculations"""

    def test_get_ev_share_2015_to_2024(self):
        """Test the get_ev_change_rate_2015_to_2024 function"""
        df_expected = pd.DataFrame(ale_input)
        df_result = get_ev_share_2015_to_2024("Kommun", to_percent=True)
        pd.testing.assert_frame_equal(df_result.iloc[:1], df_expected)

    def test_ev_share_from_2025(self):
        """Test the ev_change_rate_from_2015 function"""
        df_result = get_ev_share_from_2025("Kommun", to_percent=True)
        df_result_ale = df_result[df_result["Kommun"] == "Ale"]

        result_value = df_result_ale["evChange_2025"].iloc[0]
        expected_value = ALE_EV_SHARE_2025

        self.assertAlmostEqual(result_value, expected_value)

    def test_get_ev_change_rate_per_territory(self):
        """Test the get_ev_change_rate_per_territory function"""
        expected_value_raw = ale_expected["evChangeRate"][0]
        expected_value_float = np.float64(expected_value_raw)
        expected_value_rounded = round(expected_value_float, 4)

        # Create a Series with scalar values (extract first element from each list)
        input_series = pd.Series({k: v[0] for k, v in ale_input.items()})
        result_value = get_ev_change_rate_per_territory(input_series)
        result_value_rounded = round(result_value, 4)

        self.assertEqual(result_value_rounded, expected_value_rounded)

    def test_get_ev_change_rate(self):
        """Test the get_ev_change_rate function"""
        df_expected = pd.DataFrame(ale_expected)

        df_input = pd.DataFrame({"Kommun": ["Ale"]})
        df_result = get_ev_change_rate(df_input, "Kommun")

        pd.testing.assert_frame_equal(df_result, df_expected)


if __name__ == "__main__":
    unittest.main()
