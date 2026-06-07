"""Extracts consumption emissions from the Swedish consumption emissions Excel file."""
from pathlib import Path

import pandas as pd

PATH_SWEDISH_CONSUMPTION_EMISSIONS = (
    Path(__file__).parent / "sources" / "swedish_emissions.xlsx"
)
MUNICIPAL_HEADER_ROW = 5

SWEDISH_ABROAD_MEASURES = [
    "I Sverige",
    "Utomlands",
    "I Sverige exkl. flyg",
    "Utomlands exkl. flyg",
]


def _extract_consumption_emissions_from_excel(
    sheet_name: str, header_row: int = 0
) -> pd.DataFrame:
    """
    Extracts consumption emissions from an Excel file.

    Args:
        sheet_name (str): The name of the sheet to extract data from.
        header_row (int): The row number to use as the column header.
    """
    emissions_df = pd.read_excel(
        PATH_SWEDISH_CONSUMPTION_EMISSIONS,
        sheet_name=sheet_name,
        header=header_row,
    )

    # First column contains row labels such as "Totalt".
    first_col = emissions_df.columns[0]
    emissions_df = emissions_df.set_index(first_col)

    # Normalize year columns to ints where possible, e.g. "1990" -> 1990.
    normalized_columns = []
    for col in emissions_df.columns:
        try:
            normalized_columns.append(int(col))
        except (TypeError, ValueError):
            normalized_columns.append(col)
    emissions_df.columns = normalized_columns

    # Convert localized numeric strings only in year columns.
    for col in emissions_df.columns:
        if isinstance(col, int):
            emissions_df[col] = emissions_df[col].apply(
                lambda value: _parse_number(value) if isinstance(value, str) else value
            )

    return emissions_df


def _parse_number(value: str) -> float:
    """
    Parses a number from a string.

    Args:
        value (str): The string to parse.
    """
    return float(value.replace(" ", "").replace(".", "").replace(",", "."))


def extract_total_consumption_emissions() -> pd.DataFrame:
    """
    Extracts total consumption emissions.

    Returns:
        pandas.DataFrame: National consumption totals indexed by measure name.
    """
    return _extract_consumption_emissions_from_excel("Kons_Tot", MUNICIPAL_HEADER_ROW)


def extract_swedish_consumption_emissions() -> pd.DataFrame:
    """
    Extracts the Swedish vs abroad consumption emissions split.

    Returns:
        pandas.DataFrame: Consumption split indexed by measure name.
    """
    total_df = extract_total_consumption_emissions()
    return total_df.loc[SWEDISH_ABROAD_MEASURES]


def extract_national_household_consumption_emissions() -> pd.DataFrame:
    """
    Extracts the national household consumption total row.

    Returns:
        pandas.DataFrame: A single-row DataFrame with national household totals.
    """
    household_df = _extract_consumption_emissions_from_excel("Kons_HH", MUNICIPAL_HEADER_ROW)
    return household_df.head(1).reset_index(drop=True)


def extract_public_consumption_emissions() -> pd.DataFrame:
    """
    Extracts public consumption emissions by municipality.

    Returns:
        pandas.DataFrame: Public consumption emissions per municipality and total.
    """
    return _extract_consumption_emissions_from_excel("Kons_Off", MUNICIPAL_HEADER_ROW)


def extract_investment_consumption_emissions() -> pd.DataFrame:
    """
    Extracts investment consumption emissions by municipality.

    Returns:
        pandas.DataFrame: Investment consumption emissions per municipality and total.
    """
    return _extract_consumption_emissions_from_excel("Kons_Inv", MUNICIPAL_HEADER_ROW)


def extract_consumption_emissions_from_online_shopping() -> pd.DataFrame:
    """
    Extracts consumption emissions from online shopping.

    Returns:
        pandas.DataFrame: Online shopping emissions indexed by region.
    """
    return _extract_consumption_emissions_from_excel("E-handel", MUNICIPAL_HEADER_ROW)


def extract_emissions_from_international_flights() -> pd.DataFrame:
    """
    Extracts emissions from international flights.

    Returns:
        pandas.DataFrame: International flight emissions indexed by region.
    """
    return _extract_consumption_emissions_from_excel(
        "Utsläpp från utrikesflyg", MUNICIPAL_HEADER_ROW
    )
