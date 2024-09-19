from pathlib import Path

import polars as pl

from webapp.read import schema
from webapp.utils import get_project_root


def convert_lease(x):
    if 0 < x <= 60:
        result = "0-60 years"
    elif 60 < x <= 80:
        result = "61-80 years"
    elif 80 < x <= 99:
        result = "81-99 years"
    return result


def csv_to_parquet() -> pl.DataFrame:
    """Combine all CSV files in the specified directory into a single parquet file"""
    data_dir: Path = get_project_root() / "data"

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

    df = df.unique()
    df = df.sort(by="_id")
    df.write_parquet(data_dir / "df.parquet")
    return


if __name__ == "__main__":
    csv_to_parquet()
