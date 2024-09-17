from functools import cache
from pathlib import Path

import polars as pl
from pandas import DataFrame, concat, read_csv

from webapp.utils import get_project_root


def convert_lease(x):
    if 0 < x <= 60:
        result = "0-60 years"
    elif 60 < x <= 80:
        result = "61-80 years"
    elif 80 < x <= 99:
        result = "81-99 years"
    return result


@cache
def get_dataframe() -> pl.DataFrame:
    """Combine all CSV files in the specified directory into a single DataFrame."""
    data_dir: Path = get_project_root() / "data"

    schema = {
        "_id": pl.Int64,
        "month": pl.Utf8,
        "town": pl.Utf8,
        "flat_type": pl.Utf8,
        "block": pl.Utf8,
        "street_name": pl.Utf8,
        "storey_range": pl.Utf8,
        "floor_area_sqm": pl.Float64,
        "flat_model": pl.Utf8,
        "lease_commence_date": pl.Int64,
        "remaining_lease": pl.Utf8,
        "resale_price": pl.Float64,
        "address": pl.Utf8,
        "postal": pl.Int64,
        "latitude": pl.Float64,
        "longitude": pl.Float64,
    }

    df = pl.read_csv(data_dir / "*.csv", schema=schema, null_values="NIL")
    df = df.with_columns(
        (
            pl.col("remaining_lease")
            .str.extract(r"(\d+)", 1)
            .cast(pl.Int64)
            .alias("remaining_lease_years")
        )
    )

    df = df.with_columns(
        pl.col("remaining_lease_years")
        .map_elements(convert_lease, pl.String)
        .alias("cat_remaining_lease_years")
    )

    return df.unique()
