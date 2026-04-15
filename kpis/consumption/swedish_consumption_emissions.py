"""Extracts consumption emissions from the Swedish consumption emissions Excel file."""
from pathlib import Path
import pandas as pd

PATH_SWEDISH_CONSUMPTION_EMISSIONS = Path(__file__).parent / "sources" / "swedish_emissions.xlsx"

def _extract_consumption_emissions_from_excel(sheet_name: str, header_row: int = 0) -> pd.DataFrame:
    """
    Extracts consumption emissions from an Excel file.

    Args:
        sheet_name (str): The name of the sheet to extract data from.
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

def extract_total_consumption_emissions():
    """
    Extracts total consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.

    Returns:
        pandas.DataFrame: A DataFrame containing the extracted total consumption emissions data.
    """
    header_row = 5
    total_df = _extract_consumption_emissions_from_excel("Kons_Tot", header_row)
    return total_df

def extract_national_household_consumption_emissions():
    """
    Extracts household consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    header_row = 5
    household_df = _extract_consumption_emissions_from_excel("Kons_HH", header_row)
    total_household_df = household_df.head(1).reset_index(drop=True)
    return total_household_df

def extract_public_consumption_emissions():
    """
    Extracts public consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    header_row = 5
    public_df = _extract_consumption_emissions_from_excel("Kons_Off", header_row)
    total_row = 313
    total_official_df = public_df.iloc[[total_row]].reset_index(drop=True)
    return total_official_df

def extract_investment_consumption_emissions():
    """
    Extracts investment consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    header_row = 5
    investment_df = _extract_consumption_emissions_from_excel("Kons_Inv", header_row)
    total_row = 313
    total_investment_df = investment_df.iloc[[total_row]].reset_index(drop=True)
    return investment_df

def extract_consumption_emissions_from_online_shopping():
    """
    Extracts consumption emissions from online shopping.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    online_shopping_df = _extract_consumption_emissions_from_excel("E-handel")
    print(online_shopping_df)
    return online_shopping_df

def extract_emissions_from_international_flights():
    """
    Extracts emissions from international flights.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    international_flights_df = _extract_consumption_emissions_from_excel("Utsläpp från utrikesflyg")
    print(international_flights_df)
    return international_flights_df

def extract_swedish_consumption_emissions():
    """
    Extracts Swedish consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    Returns:
        pandas.DataFrame: A DataFrame containing the extracted Swedish consumption emissions data.
    """
    swedish_consumption_emissions_df = _extract_consumption_emissions_from_excel("Sverige")
    print(swedish_consumption_emissions_df)
    return swedish_consumption_emissions_df
