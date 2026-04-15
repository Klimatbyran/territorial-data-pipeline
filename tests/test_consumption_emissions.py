# -*- coding: utf-8 -*-
import unittest
import pandas as pd

from kpis.consumption.consumption_emissions import get_consumption_emissions


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


if __name__ == "__main__":
    unittest.main()
