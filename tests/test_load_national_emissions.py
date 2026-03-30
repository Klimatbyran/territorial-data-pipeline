# -*- coding: utf-8 -*-
"""Tests for supplementary national emission series merged into the national dataframe."""

import os
import unittest

import pandas as pd

from kpis.emissions.load_national_emissions import (
    COLUMN_NAMES,
    PATH_LOAD_SWEDISH_EMISSIONS,
    load_swedish_emissions_source,
    _extract_emissions,
)


class TestLoadNationalEmissions(unittest.TestCase):
    """Contract tests for load_national_emissions.xlsx and merge into national output."""

    def test_source_file_exists(self):
        """Test that the source file exists."""
        self.assertTrue(
            os.path.isfile(PATH_LOAD_SWEDISH_EMISSIONS),
            f"Expected workbook at {PATH_LOAD_SWEDISH_EMISSIONS}",
        )

    def test_load_summary_structure(self):
        """Test that the summary file has the correct structure."""
        emissions_df = load_swedish_emissions_source()
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
        emissions_df = load_swedish_emissions_source()
        self.assertEqual(
            emissions_df.loc["Terr_CO2e_foss", 1990], 71_260_000
        )
        self.assertEqual(
            emissions_df.loc["Terr_CO2e_bio", 1990], 22_880_000
        )

    def test_create_national_emissions_df_adds_flat_columns_and_preserves_rows(self):
        """Test that create_national_emissions_df adds flat columns and preserves rows."""
        national = pd.DataFrame([{"Land": "Sverige", "dummy": 1.0}])
        summary = load_swedish_emissions_source()
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


if __name__ == "__main__":
    unittest.main()
