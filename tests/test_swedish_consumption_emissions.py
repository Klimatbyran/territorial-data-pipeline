# -*- coding: utf-8 -*-
"""Regression tests for Swedish consumption Excel sources (swedish_emissions.xlsx)."""

import unittest

import pandas as pd

from kpis.consumption.swedish_consumption_emissions import (
    extract_consumption_emissions_from_online_shopping,
    extract_emissions_from_international_flights,
    extract_national_household_consumption_emissions,
    extract_investment_consumption_emissions,
    extract_public_consumption_emissions,
    extract_swedish_consumption_emissions,
    extract_total_consumption_emissions,
)


class TestSwedishConsumptionEmissions(unittest.TestCase):
    """Values are taken from ``kpis/consumption/sources/swedish_emissions.xlsx``."""

    def test_total_consumption_national_series(self):
        """Test the total consumption national series."""
        data_df = extract_total_consumption_emissions()
        self.assertEqual(data_df.loc["Totalt", 1990], 159639555)
        self.assertEqual(data_df.loc["Totalt", 2023], 80428937)
        self.assertEqual(data_df.loc["Totalt exkl. flyg", 2023], 79847856)
        self.assertEqual(data_df.loc["I Sverige", 2008], 39361575)

    def test_household_national_total_row(self):
        """Test the household national total row."""
        data_df = extract_national_household_consumption_emissions()
        total = data_df[data_df["Län"] == "Totalt"].iloc[0]
        self.assertEqual(total[2023], 49222283)

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

    def test_public_consumption_total(self):
        """Test the public total consumption."""
        data_df = extract_public_consumption_emissions()
        self.assertEqual(data_df.iloc[0][2023], 9132778)

    def test_investment_total(self):
        """Test the total investment consumption."""
        data_df = extract_investment_consumption_emissions()
        self.assertEqual(data_df.iloc[0][2023], 30404751)

    # def test_investment_municipality_values(self):
    #     """Test the investment municipality values."""
    #     data_df = extract_investment_consumption_emissions()
    #     self._assert_vasby_and_stockholm(data_df, 110_958, 70_989, 4_136_351)

    # def test_online_shopping_national(self):
    #     """Test the online shopping national."""
    #     data_df = extract_consumption_emissions_from_online_shopping()
    #     self.assertEqual(self._lookup_long(data_df, "Sverige", 2020), 323_350)
    #     self.assertEqual(self._lookup_long(data_df, "Sverige", 2023), 260_910)
    #     self.assertEqual(self._lookup_long(data_df, "Sverige", 2025), 325_580)

    # def test_international_flights_national(self):
    #     """Test the international flights national."""
    #     data_df = extract_emissions_from_international_flights()
    #     self.assertEqual(self._lookup_long(data_df, "Sverige", 1990), 6_976_451)
    #     self.assertEqual(self._lookup_long(data_df, "Sverige", 2023), 8_380_929)
    
    # def test_swedish_vs_abroad_split(self):
    #     """Test the swedish vs abroad split."""
    #     data_df = extract_swedish_consumption_emissions()
    #     self.assertEqual(data_df.loc["I Sverige", 2023], 28797623)
    #     self.assertEqual(data_df.loc["Utomlands", 2023], 51631314)
    #     self.assertEqual(data_df.loc["I Sverige exkl. flyg", 2023], 28532813)
    #     self.assertEqual(data_df.loc["Utomlands exkl. flyg", 2023], 51315043)


if __name__ == "__main__":
    unittest.main()
