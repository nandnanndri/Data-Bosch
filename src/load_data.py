"""Load raw SECOM files into pandas and SQLite."""
import sqlite3
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
DB = Path("data/secom.db")


def load_raw() -> pd.DataFrame:
    X = pd.read_csv(RAW / "secom.data", sep=r"\s+", header=None, na_values="NaN")
    X.columns = [f"s{i:03d}" for i in range(X.shape[1])]
    y = pd.read_csv(
        RAW / "secom_labels.data", sep=" ", header=None,
        names=["label", "timestamp"], quotechar='"',
    )
    y["timestamp"] = pd.to_datetime(y["timestamp"], format="%d/%m/%Y %H:%M:%S")
    y["fail"] = (y["label"] == 1).astype(int)
    df = pd.concat([y[["timestamp", "fail"]], X], axis=1)
    df.insert(0, "unit_id", range(len(df)))
    return df.sort_values("timestamp").reset_index(drop=True)


def to_sqlite(df: pd.DataFrame) -> None:
    with sqlite3.connect(DB) as con:
        df[["unit_id", "timestamp", "fail"]].to_sql("units", con, if_exists="replace", index=False)
        long = df.drop(columns=["timestamp", "fail"]).melt(
            id_vars="unit_id", var_name="sensor", value_name="value"
        ).dropna()
        long.to_sql("measurements", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX IF NOT EXISTS ix_meas_unit ON measurements(unit_id)")
        con.execute("CREATE INDEX IF NOT EXISTS ix_meas_sensor ON measurements(sensor)")


if __name__ == "__main__":
    df = load_raw()
    print(df.shape, "fail rate:", round(df["fail"].mean(), 4))
    print("missing share:", round(df.drop(columns=["unit_id", "timestamp", "fail"]).isna().mean().mean(), 4))
    to_sqlite(df)
