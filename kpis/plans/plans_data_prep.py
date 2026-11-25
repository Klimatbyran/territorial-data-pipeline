# -*- coding: utf-8 -*-
"""
DEPRECATED: Climate-plan columns for the website are no longer produced from
klimatplaner.xlsx. Validate municipality-sources is the source of truth; the
Unearth API overlays climatePlan* fields at request time. This module is kept
for offline analysis only and is not called by generate_data.py.
"""

import pandas as pd

from helpers import clean_kommun


PATH_PLANS_DATA = "kpis/plans/klimatplaner.xlsx"


def get_climate_plans(df):
    # LOAD CLIMATE PLANS

    df_plans = pd.read_excel(PATH_PLANS_DATA)

    # name columns after row 1
    df_plans.columns = df_plans.iloc[0]
    df_plans = df_plans.drop(0)  # drop usless rows
    df_plans = df_plans.reset_index(drop=True)

    df_plans["Kommun"] = df_plans["Kommun"].apply(clean_kommun)

    df_plans = df_plans.rename(columns={df_plans.columns[6]: "cred"})

    df_plans = df_plans.where(pd.notnull(df_plans), None)

    df = df.merge(df_plans, on="Kommun", how="left")

    return df
