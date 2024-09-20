import sys

from webapp.convert import csv_to_parquet
from webapp.extract import extract, get_timestamps
from webapp.read import get_dataframe_from_csv


def main():
    """Executes ETL process"""
    df = get_dataframe_from_csv()
    start, end = get_timestamps()
    extract([start, end, "-f"])
    csv_to_parquet()
    new_df = get_dataframe_from_csv()
    has_changed = not df.equals(new_df)

    if has_changed:
        print("Changes detected")
        sys.exit(0)
    else:
        print("No changes")
        sys.exit(1)


if __name__ == "__main__":
    main()
