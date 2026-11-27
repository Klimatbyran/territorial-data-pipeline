"""Module for retrieving political rule for municipalities.

Post-2026 styre/KSO for finished municipalities comes from SVT's
kommunstyren dataset (facts/political/svt_kommunstyren_2026.json),
sourced from https://www.svt.se/datajournalistik/de-styr-tillsammans-i-kommunerna-2026/.
Municipalities without a finished styre keep the previous mandate values.
"""
# -*- coding: utf-8 -*-

import pandas as pd


PATH_POLITICAL_RULE = "facts/political/politicalRule_mandate2026.xlsx"


def clean_municipality_name(name):
    """
    Clean the municipality name by removing whitespace and specific keywords.
    """
    # Configuration for cleaning rules
    cleaning_config = {
        "special_cases": {
            "Falu kommun": "Falun",
            "Region Gotland (kommun)": "Gotland",
            "Stockholms stad": "Stockholm",
        },
        "names_ending_with_s": {
            "Alingsås",
            "Bengtsfors",
            "Bollnäs",
            "Borås",
            "Degerfors",
            "Grums",
            "Hagfors",
            "Hällefors",
            "Hofors",
            "Höganäs",
            "Kramfors",
            "Mönsterås",
            "Munkfors",
            "Robertsfors",
            "Sotenäs",
            "Storfors",
            "Strängnäs",
            "Torsås",
            "Tranås",
            "Västerås",
            "Vännäs",
        },
        "suffixes": [" kommun", " stad"],
    }

    # Handle special cases
    if name in cleaning_config["special_cases"]:
        return cleaning_config["special_cases"][name]

    # Remove suffixes and handle 's' ending logic
    cleaned = name
    for suffix in cleaning_config["suffixes"]:
        cleaned = cleaned.replace(suffix, "")

    # Remove trailing 's' only if not in the special list
    if cleaned.endswith("s") and cleaned not in cleaning_config["names_ending_with_s"]:
        cleaned = cleaned[:-1]

    return cleaned

def clean_political_rule(rule):
    """
    Clean the political rule by removing whitespace and returning as a list.
    """
    return [item.strip() for item in rule.split(",") if item.strip()]


def get_political_rule_municipalities():
    """Get the political rule for each municipality.

    Returns:
        political_rule_df (pd.DataFrame): DataFrame with the political rule for each municipality.
    """
    raw_data_df = pd.read_excel(PATH_POLITICAL_RULE)

    raw_data_df["Kommun"] = raw_data_df["Unnamed: 1"]
    raw_data_df["KSO"] = raw_data_df["Parti KSO"]
    raw_data_df["Other"] = raw_data_df["Annat parti, ange vilket eller vilka"]
    raw_data_df = raw_data_df.filter(
        [
            "Kommun",
            "KSO",
            "SD 2026",
            "M 2026",
            "KD 2026",
            "L 2026",
            "C 2026",
            "MP 2026",
            "S 2026",
            "V 2026",
            "Other",
        ]
    )

    municipalities = []
    rules = []
    ksos = []

    party_columns = raw_data_df.columns[2:]

    for _, row in raw_data_df.iterrows():
        municipalities.append(clean_municipality_name(row["Kommun"]))

        political_rule = ",".join(
            str(row[col]) for col in party_columns if not pd.isna(row[col])
        )
        rules.append(clean_political_rule(political_rule))

        ksos.append("" if pd.isna(row["KSO"]) else row["KSO"])

    return pd.DataFrame({"Kommun": municipalities, "Rule": rules, "KSO": ksos})
