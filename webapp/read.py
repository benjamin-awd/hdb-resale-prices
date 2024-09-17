from functools import cache
from pathlib import Path

from pandas import DataFrame, concat, read_csv

from webapp.utils import get_project_root


@cache
def get_dataframe() -> DataFrame:
    """Combine all CSV files in the specified directory into a single DataFrame."""
    data_dir: Path = get_project_root() / "data"
    files = list(data_dir.glob("*.csv"))

    dfs = []

    for file in files:
        df = read_csv(file)
        dfs.append(df)

    combined_df = concat(dfs, ignore_index=True)
    return combined_df
