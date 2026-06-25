# -*- coding: utf-8 -*-
import json
import unittest
from pathlib import Path

from generate_data import create_regional_dataframe, df_to_dict
from kpis.emissions.regional_emissions import regional_emission_calculations


class TestRegionalData(unittest.TestCase):
    """Tests for regional climate data output."""

    def test_regional_emission_calculations_use_sparse_smhi_years(self):
        """Regional calculations should not require missing SMHI years 2016-2019."""
        df = regional_emission_calculations()

        self.assertEqual(len(df), 21)
        self.assertNotIn(2016, df.columns)
        self.assertNotIn(2019, df.columns)
        self.assertIn(2015, df.columns)
        self.assertIn(2020, df.columns)
        self.assertIn("historicalEmissionChangePercent", df.columns)

    def test_regional_emissions_match_municipality_year_keys(self):
        """Regional historical emissions use the same sparse SMHI year keys."""
        municipality_data = json.loads(
            Path("output/municipality-data.json").read_text(encoding="utf-8")
        )
        regional_data = df_to_dict(create_regional_dataframe(), num_decimals=2)

        municipality_years = set(municipality_data[0]["emissions"].keys())
        regional_years = set(regional_data[0]["emissions"].keys())

        self.assertEqual(regional_years, municipality_years)

    def test_regional_json_uses_total_trend_key(self):
        """Regional JSON uses totalTrend, matching municipality naming."""
        regional_data = df_to_dict(create_regional_dataframe(), num_decimals=2)
        first_region = regional_data[0]

        for year in ("2016", "2017", "2018", "2019"):
            self.assertNotIn(year, first_region["emissions"])

        self.assertIn("totalTrend", first_region)
        self.assertNotIn("total_trend", first_region)


if __name__ == "__main__":
    unittest.main()
