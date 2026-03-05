# -*- coding: utf-8 -*-

import pandas as pd


def get_electric_vehicle_per_charge_points(entity_type: str, source_path: str):
    """
    This function loads data from a CSV file provided by PowerCircle and extracts
    a DataFrame with the entity names in title case and their corresponding electric
    vehicles per charge points values.

    Returns:
        df_evpc (DataFrame): A pandas DataFrame with two columns,
        entity_type and 'EVPC', containing the entity names and their
        corresponding electric vehicles per charge points values.
    """

    df_evpc_raw = pd.read_csv(source_path)
    df_evpc_raw = df_evpc_raw.rename(columns={"Unnamed: 0": entity_type})

    # Calculate reciprocals of EVCP values
    df_evpc_raw["EVPC"] = df_evpc_raw.apply(
        lambda row: (
            row["Antal laddbara fordon"] / row["Antal laddpunkter"]
            if row["Antal laddpunkter"] != 0
            else None
        ),
        axis=1,
    )

    df_evpc = df_evpc_raw[[entity_type, "EVPC"]]

    return df_evpc
