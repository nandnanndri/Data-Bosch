"""Cleaning and feature preparation for SECOM."""
import sqlite3

import numpy as np
import pandas as pd


def load_wide(db="data/secom.db") -> pd.DataFrame:
    with sqlite3.connect(db) as con:
        units = pd.read_sql("SELECT * FROM units", con, parse_dates=["timestamp"])
        meas = pd.read_sql("SELECT * FROM measurements", con)
    wide = meas.pivot(index="unit_id", columns="sensor", values="value")
    return units.merge(wide, on="unit_id", how="left").sort_values("timestamp").reset_index(drop=True)


def drop_bad_sensors(df: pd.DataFrame, max_missing=0.4):
    sensors = [c for c in df.columns if c.startswith("s")]
    miss = df[sensors].isna().mean()
    const = df[sensors].nunique(dropna=True) <= 1
    keep = [s for s in sensors if miss[s] <= max_missing and not const[s]]
    return df[["unit_id", "timestamp", "fail"] + keep], keep


def time_split(df: pd.DataFrame, test_frac=0.2):
    cut = int(len(df) * (1 - test_frac))
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()
