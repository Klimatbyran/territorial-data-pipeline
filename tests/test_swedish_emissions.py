# -*- coding: utf-8 -*-
"""Tests for supplementary national emission series merged into the national dataframe."""

import os
import unittest
from unittest.mock import patch

import pandas as pd

from kpis.emissions.swedish_emissions import (
    COLUMN_NAMES,
    PATH_LOAD_SWEDISH_EMISSIONS,
    _load_swedish_emissions_source,
    _extract_emissions,
    _calculate_total_emissions,
)


class TestSwedishEmissions(unittest.TestCase):
    """Contract tests for swedish_emissions.xlsx and merge into national output."""

    def test_source_file_exists(self):
        """Test that the source file exists."""
        self.assertTrue(
            os.path.isfile(PATH_LOAD_SWEDISH_EMISSIONS),
            f"Expected workbook at {PATH_LOAD_SWEDISH_EMISSIONS}",
        )

    def test_load_summary_structure(self):
        """Test that the summary file has the correct structure."""
        emissions_df = _load_swedish_emissions_source()
        self.assertGreater(
            len(emissions_df.index), 0, "Expected at least one variable row"
        )
        self.assertGreater(
            len(emissions_df.columns), 0, "Expected at least one year column"
        )

        year_cols = [c for c in emissions_df.columns if isinstance(c, (int, float))]
        self.assertTrue(all(isinstance(int(y), int) for y in year_cols))
        self.assertEqual(min(year_cols), 1990)
        self.assertGreaterEqual(max(year_cols), 2023)

        expected_vars = {
            "Terr_CO2e_foss",
            "Terr_CO2e_bio",
            "Kons_utlandet",
            "Export av oljeprodukter",
        }
        self.assertTrue(
            expected_vars.issubset(set(emissions_df.index)),
            f"Missing expected variables; have {set(emissions_df.index)}",
        )

    def test_swedish_thousands_parsed_as_float(self):
        """Test that the Swedish thousands are parsed as floats."""
        emissions_df = _load_swedish_emissions_source()
        self.assertEqual(
            emissions_df.loc["Terr_CO2e_foss", 1990], 71_260_000
        )
        self.assertEqual(
            emissions_df.loc["Terr_CO2e_bio", 1990], 22_880_000
        )

    def test_create_national_emissions_df_adds_flat_columns_and_preserves_rows(self):
        """Test that create_national_emissions_df adds flat columns and preserves rows."""
        national = pd.DataFrame([{"Land": "Sverige", "dummy": 1.0}])
        summary = _load_swedish_emissions_source()
        emissions_df = _extract_emissions()

        self.assertEqual(len(emissions_df), 1)

        original_cols = set(national.columns)
        extra = [c for c in emissions_df.columns if c not in original_cols]
        self.assertEqual(
            len(extra),
            len(COLUMN_NAMES) * len(summary.columns),
            "Each variable × year should produce one merged column",
        )
        self.assertIn("biogenic_1990", emissions_df.columns)
        self.assertAlmostEqual(
            emissions_df["biogenic_1990"].iloc[0],
            summary.loc["Terr_CO2e_bio", 1990],
            places=3,
        )
    def _make_emissions_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "fossil_2020": 1000.0,
                    "biogenic_2020": 200.0,
                    "consumption_2020": 300.0,
                    "fossil_2021": 1100.0,
                    "biogenic_2021": 210.0,
                    "consumption_2021": 310.0,
                }
            ]
        )

    def test_total_columns_are_created_for_each_year(self):
        """A ``total_<year>`` column must exist for every year present in the input."""
        input_df = self._make_emissions_df()
        result = _calculate_total_emissions(input_df)
        self.assertIn("total_2020", result.columns)
        self.assertIn("total_2021", result.columns)

    def test_total_values_are_correct_sums(self):
        """Each ``total_<year>`` value must equal the sum of all ``*_<year>`` columns."""
        input_df = self._make_emissions_df()
        result = _calculate_total_emissions(input_df)
        self.assertAlmostEqual(result["total_2020"].iloc[0], 1500.0, places=6)
        self.assertAlmostEqual(result["total_2021"].iloc[0], 1620.0, places=6)

    def test_original_columns_are_preserved(self):
        """Input columns must still be present after the function runs."""
        input_df = self._make_emissions_df()
        original_cols = set(input_df.columns)
        result = _calculate_total_emissions(input_df)
        self.assertTrue(original_cols.issubset(set(result.columns)))

    def test_single_variable_total_equals_that_variable(self):
        """With only one variable per year the total must equal that variable's value."""
        single_var_df = pd.DataFrame([{"fossil_1990": 71_260_000.0}])
        result = _calculate_total_emissions(single_var_df)
        self.assertAlmostEqual(
            result["total_1990"].iloc[0], 71_260_000.0, places=3
        )

    def test_nan_values_are_treated_as_zero_in_sum(self):
        """pandas sum(axis=1) skips NaN by default,
        a year with one NaN column still sums the rest."""
        nan_df = pd.DataFrame([{"fossil_2000": float("nan"), "biogenic_2000": 500.0}])
        result = _calculate_total_emissions(nan_df)
        self.assertAlmostEqual(result["total_2000"].iloc[0], 500.0, places=6)

    def test_no_extra_years_introduced(self):
        """No ``total_<year>`` columns must appear for years not in the input."""
        emissions_df = self._make_emissions_df()
        result = _calculate_total_emissions(emissions_df)
        total_years = {
            int(col.split("_")[1])
            for col in result.columns
            if col.startswith("total_")
        }
        self.assertEqual(total_years, {2020, 2021})


if __name__ == "__main__":
    unittest.main()
