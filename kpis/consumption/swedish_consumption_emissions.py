"""Extracts consumption emissions from the Swedish consumption emissions Excel file."""
from pathlib import Path
import pandas as pd

PATH_SWEDISH_CONSUMPTION_EMISSIONS = Path(__file__).parent / "sources" / "swedish_emissions.xlsx"

def _extract_consumption_emissions_from_excel(sheet_name: str) -> pd.DataFrame:
    """
    Extracts consumption emissions from an Excel file.

    Args:
        sheet_name (str): The name of the sheet to extract data from.
    """
    return pd.read_excel(PATH_SWEDISH_CONSUMPTION_EMISSIONS, sheet_name=sheet_name)

def extract_total_consumption_emissions():
    """
    Extracts total consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.

    Returns:
        pandas.DataFrame: A DataFrame containing the extracted total consumption emissions data.
    """
    total_df = _extract_consumption_emissions_from_excel("Kons_Tot")
    print(total_df)
    return total_df

def extract_household_consumption_emissions():
    """
    Extracts household consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    household_df = _extract_consumption_emissions_from_excel("Kons_HH")
    print(household_df)
    return household_df

def extract_public_consumption_emissions():
    """
    Extracts public consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    public_df = _extract_consumption_emissions_from_excel("Kons_Off")
    print(public_df)
    return public_df

def extract_investment_consumption_emissions():
    """
    Extracts investment consumption emissions.

    Args:
        df (pandas.DataFrame): The input DataFrame containing consumption emissions data.
    """
    investment_df = _extract_consumption_emissions_from_excel("Kons_Inv")
    print(investment_df)
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
