# -*- coding: utf-8 -*-
"""Tests for supplementary national emission series merged into the national dataframe."""

import os
import unittest
from unittest.mock import patch

import pandas as pd

from kpis.emissions.swedish_emissions import (
    COLUMN_NAMES,
    E_HANDEL_YEARS,
    PATH_LOAD_SWEDISH_EMISSIONS,
    _load_e_handel_emissions_source,
    _load_swedish_emissions_source,
    _load_territorial_emissions_source,
    _extract_emissions,
    _calculate_total_emissions,
    create_swedish_emissions_df,
)
from generate_data import national_df_to_dict


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
        self.assertGreaterEqual(max(year_cols), 2025)

        expected_vars = {
            "Produktionsbaserade utsläpp",
            "Biogena utsläpp",
            "Konsumtionsbaserade utsläpp i utlandet",
            "Utsläpp i utlandet pga export av oljeprodukter",
        }
        self.assertTrue(
            expected_vars.issubset(set(emissions_df.index)),
            f"Missing expected variables; have {set(emissions_df.index)}",
        )

    def test_territorial_emissions_in_national_output(self):
        """Territorial emissions are exported as territorialFossilEmissions in national JSON."""
        territorial = _load_territorial_emissions_source()
        national_df = create_swedish_emissions_df()
        national_df["coatOfArms"] = "https://example.com/coat.svg"
        national_data = national_df_to_dict(national_df, 2)[0]

        self.assertIn("territorialFossilEmissions", national_data)
        output = national_data["territorialFossilEmissions"]

        self.assertEqual(list(territorial.index), list(range(1990, 2026)))
        self.assertEqual(
            sorted(output.keys()),
            [str(year) for year in territorial.index],
        )
        self.assertTrue(all(value > 0 for value in output.values()))

        spot_checks = {
            1990: 71_230_000,
            2000: 68_110_000,
            2010: 64_170_000,
            2020: 46_380_000,
            2023: 44_820_000,
            2024: 48_060_000,
            2025: 46_730_000,
        }
        for year, expected in spot_checks.items():
            self.assertEqual(
                output[str(year)],
                expected,
                f"Unexpected territorial value for {year}",
            )
            self.assertEqual(
                output[str(year)],
                territorial[year],
                f"National output diverged from Terr_GHG for {year}",
            )

        self.assertNotEqual(
            output["1990"],
            national_data["productionBasedEmissions"]["1990"],
            "Territorial and production-based 1990 values should differ",
        )

    def test_load_territorial_emissions_from_terr_ghg(self):
        """Territorial fossil values come from the Terr_GHG national row."""
        territorial_df = _load_territorial_emissions_source()
        self.assertEqual(territorial_df[1990], 71_230_000)
        self.assertEqual(territorial_df[2024], 48_060_000)
        self.assertEqual(territorial_df[2025], 46_730_000)

    def test_extract_emissions_includes_territorial_and_production_columns(self):
        """Flattened emissions expose territorial and production-based series separately."""
        emissions_df = _extract_emissions()
        summary = _load_swedish_emissions_source()
        territorial = _load_territorial_emissions_source()

        self.assertEqual(emissions_df["fossil_1990"].iloc[0], territorial[1990])
        self.assertEqual(
            emissions_df["production_based_1990"].iloc[0],
            summary.loc["Produktionsbaserade utsläpp", 1990],
        )
        self.assertNotEqual(
            emissions_df["fossil_1990"].iloc[0],
            emissions_df["production_based_1990"].iloc[0],
        )

    def test_swedish_thousands_parsed_as_float(self):
        """Test that the Swedish thousands are parsed as floats."""
        emissions_df = _load_swedish_emissions_source()
        self.assertEqual(
            emissions_df.loc["Produktionsbaserade utsläpp", 1990], 73_268_216
        )
        self.assertEqual(
            emissions_df.loc["Biogena utsläpp", 1990], 22_880_000
        )

    def test_e_handel_sheet_loads_2020_to_2025(self):
        """E-handel sheet exposes national e-commerce emissions for 2020–2025."""
        emissions_df = _load_e_handel_emissions_source()
        self.assertEqual(list(emissions_df.columns), E_HANDEL_YEARS)
        self.assertEqual(emissions_df.index.tolist(), ["Sverige"])
        expected = {
            2020: 323_350,
            2021: 323_350,
            2022: 256_450,
            2023: 260_910,
            2024: 403_630,
            2025: 325_580,
        }
        for year, value in expected.items():
            self.assertEqual(
                emissions_df.loc["Sverige", year],
                value,
                f"Unexpected e-handel value for {year}",
            )

    def test_extract_emissions_includes_e_commerce_columns(self):
        """Flattened emissions include e_commerce_<year> for each E-handel year."""
        emissions_df = _extract_emissions()
        for year in E_HANDEL_YEARS:
            col = f"e_commerce_{year}"
            self.assertIn(col, emissions_df.columns)
            self.assertEqual(
                emissions_df[col].iloc[0],
                _load_e_handel_emissions_source().loc["Sverige", year],
            )

    def test_create_national_emissions_df_adds_flat_columns_and_preserves_rows(self):
        """Test that create_national_emissions_df adds flat columns and preserves rows."""
        national = pd.DataFrame([{"Land": "Sverige", "dummy": 1.0}])
        summary = _load_swedish_emissions_source()
        territorial = _load_territorial_emissions_source()
        emissions_df = _extract_emissions()

        self.assertEqual(len(emissions_df), 1)

        original_cols = set(national.columns)
        extra = [c for c in emissions_df.columns if c not in original_cols]
        e_handel_cols = [f"e_commerce_{y}" for y in E_HANDEL_YEARS]
        mapped_variables = [v for v in summary.index if v in COLUMN_NAMES]
        expected_count = (
            len(mapped_variables) * len(summary.columns)
            + len(territorial.index)
            + len(e_handel_cols)
        )
        self.assertEqual(
            len(extra),
            expected_count,
            "Each variable × year plus e-commerce years should produce one merged column",
        )
        self.assertIn("biogenic_1990", emissions_df.columns)
        self.assertIn("production_based_1990", emissions_df.columns)
        self.assertIn("fossil_1990", emissions_df.columns)
        self.assertAlmostEqual(
            emissions_df["biogenic_1990"].iloc[0],
            summary.loc["Biogena utsläpp", 1990],
            places=3,
        )
    def _make_emissions_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "production_based_2020": 1000.0,
                    "biogenic_2020": 200.0,
                    "consumption_2020": 300.0,
                    "production_based_2021": 1100.0,
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
        """With only one non-territorial variable per year the total equals that value."""
        single_var_df = pd.DataFrame([{"production_based_1990": 71_260_000.0}])
        result = _calculate_total_emissions(single_var_df)
        self.assertAlmostEqual(
            result["total_1990"].iloc[0], 71_260_000.0, places=3
        )

    def test_territorial_fossil_is_excluded_from_total(self):
        """Territorial fossil values are reported separately and not summed into total."""
        df = pd.DataFrame(
            [
                {
                    "fossil_1990": 71_230_000.0,
                    "production_based_1990": 73_268_216.0,
                    "biogenic_1990": 22_880_000.0,
                }
            ]
        )
        result = _calculate_total_emissions(df)
        self.assertAlmostEqual(
            result["total_1990"].iloc[0],
            73_268_216.0 + 22_880_000.0,
            places=3,
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
