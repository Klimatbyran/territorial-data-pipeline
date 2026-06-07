# -*- coding: utf-8 -*-
import unittest
import pandas as pd

from kpis.consumption.consumption_emissions import (
    get_consumption_emissions,
    get_regional_consumption_emissions,
)


class TestConsumtionEmissionsCalculations(unittest.TestCase):
    """Test class for consumption emissions calculations."""

    def test_get_consumption_emissions(self):
        """Test that get_consumption_emissions returns correct data."""
        df_expected = pd.DataFrame(
            {
                "Kommun": ["Ale", "Alingsås", "Alvesta"],
                "consumption_emissions": [
                    5.3145,
                    5.3058,
                    5.0665,
                ],
            }
        )

        df_result = get_consumption_emissions()
        df_result_sorted = df_result.sort_values(by="Kommun").reset_index(drop=True)

        pd.testing.assert_frame_equal(df_result_sorted.iloc[:3], df_expected)

    def test_get_regional_consumption_emissions(self):
        """Test that get_regional_consumption_emissions returns län-level data."""
        df_expected = pd.DataFrame(
            {
                "Län": ["Blekinge län", "Dalarnas län", "Gotlands län"],
                "consumption_emissions": [5.1836, 5.3801, 5.1309],
            }
        )

        df_result = get_regional_consumption_emissions()
        df_result_sorted = df_result.sort_values(by="Län").reset_index(drop=True)

        self.assertEqual(len(df_result), 21)
        pd.testing.assert_frame_equal(df_result_sorted.iloc[:3], df_expected)


if __name__ == "__main__":
    unittest.main()
