# -*- coding: utf-8 -*-
"""Tests for supplementary national emission series merged into the national dataframe."""

import os
import unittest

import pandas as pd

from kpis.emissions.additional_national_emissions import (
    PATH_ADDITIONAL_NATIONAL_EMISSIONS,
    load_additional_national_emissions_summary,
    merge_additional_national_emissions_into_national_df,
)


class TestAdditionalNationalEmissions(unittest.TestCase):
    """Contract tests for additional_national_emissions.xlsx and merge into national output."""

    def test_source_file_exists(self):
        """Test that the source file exists."""
        self.assertTrue(
            os.path.isfile(PATH_ADDITIONAL_NATIONAL_EMISSIONS),
            f"Expected workbook at {PATH_ADDITIONAL_NATIONAL_EMISSIONS}",
        )

    def test_load_summary_structure(self):
        """Test that the summary file has the correct structure."""
        additional_emissions_df = load_additional_national_emissions_summary()
        self.assertGreater(
            len(additional_emissions_df.index), 0, "Expected at least one variable row"
        )
        self.assertGreater(
            len(additional_emissions_df.columns), 0, "Expected at least one year column"
        )

        year_cols = [c for c in additional_emissions_df.columns if isinstance(c, (int, float))]
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
            expected_vars.issubset(set(additional_emissions_df.index)),
            f"Missing expected variables; have {set(additional_emissions_df.index)}",
        )

    def test_swedish_thousands_parsed_as_float(self):
        """Test that the Swedish thousands are parsed as floats."""
        additional_emissions_df = load_additional_national_emissions_summary()
        self.assertEqual(
            additional_emissions_df.loc["Terr_CO2e_foss", 1990], 71_260_000
        )
        self.assertEqual(
            additional_emissions_df.loc["Terr_CO2e_bio", 1990], 22_880_000
        )

    def test_merge_adds_flat_columns_and_preserves_rows(self):
        """Test that the merge adds flat columns and preserves rows."""
        national = pd.DataFrame([{"Land": "Sverige", "dummy": 1.0}])
        summary = load_additional_national_emissions_summary()
        merged = merge_additional_national_emissions_into_national_df(
            national, summary_df=summary
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged["Land"].iloc[0], "Sverige")

        extra = [c for c in merged.columns if c.startswith("additional_national_")]
        self.assertEqual(
            len(extra),
            len(summary.index) * len(summary.columns),
            "Each variable × year should produce one merged column",
        )
        self.assertIn("additional_national_Terr_CO2e_foss_1990", merged.columns)
        self.assertAlmostEqual(
            merged["additional_national_Terr_CO2e_foss_1990"].iloc[0],
            summary.loc["Terr_CO2e_foss", 1990],
            places=3,
        )


if __name__ == "__main__":
    unittest.main()
