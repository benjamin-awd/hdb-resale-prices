import sys
from pathlib import Path

import polars as pl

from webapp.read import get_project_root, schema
from webapp.update.convert import csv_to_parquet
from webapp.update.extract import extract, get_timestamps


def update_data():
    """Executes ETL process"""
    csv_file_glob: Path = get_project_root() / "data" / "*.csv"
    df = pl.read_csv(csv_file_glob, schema=schema)

    start, end = get_timestamps()
    extract([start, end, "-f"])
    csv_to_parquet()
    new_df = pl.read_csv(csv_file_glob, schema=schema)
    has_changed = not df.equals(new_df)

    if has_changed:
        print("Changes detected")
    sys.exit(0)


if __name__ == "__main__":
    update_data()
