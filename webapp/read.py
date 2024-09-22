from functools import cache
from pathlib import Path

import polars as pl

from webapp.utils import get_project_root


def convert_lease(x):
    if 0 < x <= 60:
        result = "0-60 years"
    elif 60 < x <= 80:
        result = "61-80 years"
    elif 80 < x <= 99:
        result = "81-99 years"
    return result


def get_dataframe_from_csv() -> pl.DataFrame:
    """Combine all CSV files in the specified directory into a single DataFrame."""
    data_dir: Path = get_project_root() / "data"

    df = pl.read_csv(data_dir / "*.csv", schema=schema, null_values="NIL")
    return df


def get_dataframe_from_parquet() -> pl.DataFrame:
    """Combine all CSV files in the specified directory into a single DataFrame."""
    data_dir: Path = get_project_root() / "data"

    df = pl.read_parquet(data_dir / "df.parquet")
    df = df.with_columns(
        pl.when(pl.col("address").str.contains("HOLLAND"))
        .then(pl.lit("HOLLAND"))
        .otherwise(pl.col("town"))
        .alias("town")
    )
    return df.sort(by="town")


def load_dataframe() -> pl.DataFrame:
    """Wrapper for get_dataframe that provides a cache"""
    df = get_dataframe_from_parquet()
    return df.with_columns(pl.col("month").str.strptime(pl.Date, "%Y-%m"))


schema = {
    "_id": pl.Int64,
    "month": pl.Utf8,
    "town": pl.Utf8,
    "flat_type": pl.Utf8,
    "block": pl.Utf8,
    "street_name": pl.Utf8,
    "storey_range": pl.Utf8,
    "floor_area_sqm": pl.Float32,
    "flat_model": pl.Utf8,
    "lease_commence_date": pl.Int16,
    "remaining_lease": pl.Utf8,
    "resale_price": pl.Float32,
    "address": pl.Utf8,
    "postal": pl.Int32,
    "latitude": pl.Float32,
    "longitude": pl.Float32,
}
