from datetime import datetime

import pandas as pd
import streamlit as st

from webapp.logo import logo
from webapp.read import load_dataframe
from webapp.utils import get_project_root

st.set_page_config(page_title="HDB Resale Prices", layout="wide")
data = pd.read_csv("data.csv", index_col=0)
earliest_date = min(data["month"])
latest_date = max(data["month"])
range_date = earliest_date + " to " + latest_date

st.image(logo, width=800)

st.markdown(
    """## Resale Visualizations
Make better decisions using data from the latest HDB resale market movements
"""
)

df = load_dataframe()

st.write(
    "Source: [data.gov.sg](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view)",
)

data_dir = get_project_root() / "data"
with open(data_dir / "metadata") as file:
    content = int(file.read())
    last_updated = datetime.fromtimestamp(content)
    st.write(f"Last updated: {last_updated}")
