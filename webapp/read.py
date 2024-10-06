from datetime import datetime
from pathlib import Path

import polars as pl
import streamlit as st
from pybadges import badge

from webapp.utils import get_project_root


def get_last_updated_badge():
    data_dir = get_project_root() / "data"
    with open(data_dir / "metadata") as file:
        content = int(file.read())
        last_updated = datetime.fromtimestamp(content)

    return badge(
        left_text="last updated",
        right_text=last_updated.isoformat()[:10],
        left_color="#555",
        right_color="#007ec6",
    )


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

    df = pl.read_csv(data_dir / "*.csv", schema=schema)
    return df


def get_dataframe_from_parquet() -> pl.DataFrame:
    """Combine all CSV files in the specified directory into a single DataFrame."""
    data_dir: Path = get_project_root() / "data"

    df = pl.read_parquet(data_dir / "df.parquet")
    return df.sort(by="town")


def add_time_filters(df: pl.DataFrame):
    df = df.with_columns(pl.col("month").str.strptime(pl.Date, "%Y-%m"))
    df = df.with_columns(
        pl.col("month").dt.quarter().alias("quarter"),
        pl.col("month").dt.year().alias("year"),
    )

    df = df.with_columns(
        (
            pl.concat_str(
                [
                    pl.col("year").cast(str),
                    pl.col("quarter")
                    .cast(str)
                    .map_elements(lambda x: f" Q{x}", return_dtype=str),
                ]
            ).alias("quarter_label")
        )
    )
    return df


@st.cache_data
def load_dataframe() -> pl.DataFrame:
    """Wrapper for get_dataframe that provides a cache"""
    df = get_dataframe_from_parquet()
    df = add_time_filters(df)
    return df


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
