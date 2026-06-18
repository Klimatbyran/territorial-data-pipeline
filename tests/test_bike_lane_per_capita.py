"""Test the bicycle calculations"""
# -*- coding: utf-8 -*-
import unittest
import pandas as pd

from kpis.bicycles.bicycle_data_calculations import calculate_bike_lane_per_capita


class TestBicycleCalculations(unittest.TestCase):
    """Test the bicycle calculations"""

    def test_calculate_bike_lane_per_capita(self):
        """Test the calculate_bike_lane_per_capita function"""
        df_expected = pd.DataFrame(
            {
                "Kommun": ["Ale", "Alingsås", "Alvesta"],
                "bike_metre_per_capita": [
                    93659.5905567387 / 32620,
                    125166.51428532 / 42861,
                    68335.9434684539 / 19687,
                ],
            }
        )

        df_result = calculate_bike_lane_per_capita()

        pd.testing.assert_frame_equal(
            df_result.iloc[:3], df_expected, check_dtype=False, rtol=1e-4, atol=1e-4
        )


if __name__ == "__main__":
    unittest.main()
