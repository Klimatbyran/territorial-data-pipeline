# -*- coding: utf-8 -*-
"""Regression tests for Swedish consumption Excel sources (swedish_emissions.xlsx)."""

import unittest

import pandas as pd

from kpis.consumption.swedish_consumption_emissions import (
    extract_consumption_emissions_from_online_shopping,
    extract_emissions_from_international_flights,
    extract_household_consumption_emissions,
    extract_investment_consumption_emissions,
    extract_public_consumption_emissions,
    extract_swedish_consumption_emissions,
    extract_total_consumption_emissions,
)


class TestSwedishConsumptionEmissions(unittest.TestCase):
    """Values are taken from ``kpis/consumption/sources/swedish_emissions.xlsx``."""

    def _lookup_long(self, data_df: pd.DataFrame, measure: str, year: int) -> float:
        """Lookup a value in the dataframe."""
        row = data_df[(data_df["measure"] == measure) & (data_df["year"] == year)]
        self.assertEqual(len(row), 1, msg=f"missing {measure!r} {year}")
        return float(row["value"].iloc[0])

    def test_total_consumption_national_series(self):
        """Test the total consumption national series."""
        data_df = extract_total_consumption_emissions()
        self.assertEqual(self._lookup_long(data_df, "Totalt", 1990), 159_639_555)
        self.assertEqual(self._lookup_long(data_df, "Totalt", 2023), 80_428_937)
        self.assertEqual(self._lookup_long(data_df, "Totalt exkl. flyg", 2023), 79_847_856)

    def test_swedish_vs_abroad_split(self):
        """Test the swedish vs abroad split."""
        data_df = extract_swedish_consumption_emissions()
        self.assertEqual(self._lookup_long(data_df, "I Sverige", 2023), 28_797_623)
        self.assertEqual(self._lookup_long(data_df, "Utomlands", 2023), 51_631_314)
        self.assertEqual(self._lookup_long(data_df, "I Sverige exkl. flyg", 2023), 28_532_813)
        self.assertEqual(self._lookup_long(data_df, "Utomlands exkl. flyg", 2023), 51_315_043)

    def test_household_national_total_row(self):
        """Test the household national total row."""
        data_df = extract_household_consumption_emissions()
        total = data_df[data_df["municipality"] == "Totalt"].iloc[0]
        self.assertEqual(total[2023], 49_222_283)

    def _assert_vasby_and_stockholm(
        self,
        data_df: pd.DataFrame,
        vasby_2008: int,
        vasby_2023: int,
        stockholm_2023: int,
    ) -> None:
        vasby = data_df[data_df["municipality"] == "Upplands Väsby"].iloc[0]
        self.assertEqual(vasby[2008], vasby_2008)
        self.assertEqual(vasby[2023], vasby_2023)
        stockholm = data_df[data_df["municipality"] == "Stockholm"].iloc[0]
        self.assertEqual(stockholm[2023], stockholm_2023)

    def test_public_municipality_values(self):
        """Test the public municipality values."""
        data_df = extract_public_consumption_emissions()
        self._assert_vasby_and_stockholm(data_df, 44_817, 29_371, 1_711_363)

    def test_investment_municipality_values(self):
        """Test the investment municipality values."""
        data_df = extract_investment_consumption_emissions()
        self._assert_vasby_and_stockholm(data_df, 110_958, 70_989, 4_136_351)

    def test_online_shopping_national(self):
        """Test the online shopping national."""
        data_df = extract_consumption_emissions_from_online_shopping()
        self.assertEqual(self._lookup_long(data_df, "Sverige", 2020), 323_350)
        self.assertEqual(self._lookup_long(data_df, "Sverige", 2023), 260_910)
        self.assertEqual(self._lookup_long(data_df, "Sverige", 2025), 325_580)

    def test_international_flights_national(self):
        """Test the international flights national."""
        data_df = extract_emissions_from_international_flights()
        self.assertEqual(self._lookup_long(data_df, "Sverige", 1990), 6_976_451)
        self.assertEqual(self._lookup_long(data_df, "Sverige", 2023), 8_380_929)


if __name__ == "__main__":
    unittest.main()
