# -*- coding: utf-8 -*-
import unittest

from kpis.emissions.historical_data_calculations import get_n_prep_national_data_from_smhi
from kpis.emissions.national_emissions import national_emission_calculations


class TestNationalEmissions(unittest.TestCase):
    """Test fetching and calculations of national emission data"""

    def test_get_n_prep_national_data_from_smhi(self):
        """Test that the national SMHI data has the correct structure and expected year range."""
        df_result = get_n_prep_national_data_from_smhi()

        # Check that we have exactly one row (national level)
        self.assertEqual(len(df_result), 1, "National data should have exactly one row")

        # Check that Land column exists and has correct value
        self.assertTrue("Land" in df_result.columns, "Land column should exist")
        self.assertEqual(df_result["Land"].iloc[0], "Sverige", "Land should be 'Sverige'")

        # Check that categorical columns exist (they are kept in the dataframe)
        self.assertTrue("Huvudsektor" in df_result.columns, "Huvudsektor column should exist")
        self.assertTrue("Undersektor" in df_result.columns, "Undersektor column should exist")
        self.assertTrue("Län" in df_result.columns, "Län column should exist")
        self.assertTrue("Kommun" in df_result.columns, "Kommun column should exist")

        # Check that categorical columns have expected values
        self.assertEqual(df_result["Huvudsektor"].iloc[0], "Alla", "Huvudsektor should be 'Alla'")
        self.assertEqual(df_result["Undersektor"].iloc[0], "Alla", "Undersektor should be 'Alla'")
        self.assertEqual(df_result["Län"].iloc[0], "Alla", "Län should be 'Alla'")
        self.assertEqual(df_result["Kommun"].iloc[0], "Alla", "Kommun should be 'Alla'")

        # Check for expected year columns
        result_columns = [col for col in df_result.columns if str(col).isdigit()]
        expected_columns = [
            1990,
            2000,
            2005,
            2010,
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
            2021,
            2022,
            2023,
        ]

        # Check that the expected columns are in the dataframe
        self.assertEqual(
            result_columns,
            expected_columns,
            f"Expected year columns {expected_columns}, got {result_columns}",
        )

        # Each of the column values should all be greater than 0.0
        self.assertTrue(
            (df_result[expected_columns] > 0.0).all().all(),
            "All emission values should be greater than 0",
        )

    def test_national_emission_calculations(self):
        """Test that national emission calculations return verified SMHI historical data only."""
        df_result = national_emission_calculations()

        self.assertEqual(len(df_result), 1, "National calculations should have exactly one row")
        self.assertEqual(df_result["Land"].iloc[0], "Sverige", "Land should be 'Sverige'")

        expected_year_columns = [
          1990, 2000, 2005, 2010, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
        ]
        missing_columns = set(expected_year_columns) - set(df_result.columns)
        self.assertEqual(
            len(missing_columns),
            0,
            f"Missing year columns: {missing_columns}",
        )

        excluded_columns = [
            "total_trend",
            "totalCarbonLawPath",
            "historicalEmissionChangePercent",
            "meetsParisGoal",
        ]
        for col in excluded_columns:
            self.assertNotIn(col, df_result.columns, f"Unexpected column: {col}")

        approximated_columns = [
            col for col in df_result.columns if "approximated_" in str(col)
        ]
        self.assertEqual(
            approximated_columns,
            [],
            "National SMHI data should not include approximated columns",
        )

        trend_columns = [
            col
            for col in df_result.columns
            if "trend_" in str(col) and "coefficient" not in str(col) and "slope" not in str(col)
        ]
        self.assertEqual(
            trend_columns,
            [],
            "National SMHI data should not include trend projection columns",
        )


if __name__ == "__main__":
    unittest.main()
