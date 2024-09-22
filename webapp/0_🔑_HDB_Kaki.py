from datetime import datetime

import plotly.express as px
import polars as pl
import pybadges
import streamlit as st

from webapp.filter import SidebarFilter
from webapp.logo import icon, logo
from webapp.read import load_dataframe
from webapp.utils import get_project_root

st.set_page_config(page_title="HDB Kaki", page_icon=icon, layout="wide")

st.image(logo, width=500)

data_dir = get_project_root() / "data"
with open(data_dir / "metadata") as file:
    content = int(file.read())
    last_updated = datetime.fromtimestamp(content)

last_updated_badge = pybadges.badge(
    left_text="last updated",
    right_text=last_updated.isoformat()[:10],
    left_color="#555",
    right_color="#007ec6",
)
st.image(last_updated_badge)

st.markdown("## Resale Visualizations")

st.markdown("Make better decisions using the latest HDB resale market movements")

df = load_dataframe()

sf = SidebarFilter(
    df,
    min_date=df["month"].min(),
    select_towns=(True, "multi"),
    select_lease_years=False,
)

chart_df = (
    sf.df.with_columns(
        pl.col("month").dt.quarter().alias("quarter"),
        pl.col("month").dt.year().alias("year"),
    )
    .group_by(["year", "quarter", "cat_remaining_lease_years"])
    .agg(pl.median("resale_price").alias("median_resale_price"))
    .sort(["cat_remaining_lease_years", "year", "quarter"])
)

# Calculate percentage change
chart_df = chart_df.with_columns(
    (
        (
            pl.col("median_resale_price")
            / pl.first("median_resale_price").over("cat_remaining_lease_years")
            - 1
        )
        * 100
    ).alias("percentage_change")
)

# Create a new column for quarter labels (e.g., Q1 2022)
chart_df = chart_df.with_columns(
    (
        pl.concat_str(
            [
                pl.col("year").cast(str),
                pl.col("quarter").cast(str).map_elements(lambda x: f" Q{x}"),
            ]
        ).alias("quarter_label")
    )
)

# Plot
fig = px.line(
    chart_df,
    x="quarter_label",
    y="percentage_change",
    color="cat_remaining_lease_years",
    title=f"Percentage Change in Median Resale Price since {sf.start_date}",
    labels={
        "percentage_change": "Percentage Change (%)",
        "quarter_label": "Quarter",
        "cat_remaining_lease_years": "Remaining Lease Years",
    },
)

fig.update_yaxes(ticksuffix="%")
fig.update_traces(hovertemplate="%{y:.2f}%")
source = "Source: <a href='https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view'>data.gov.sg</a>"

fig.update_layout(
    hovermode="x unified",
    annotations=[
        dict(
            x=0.5,
            y=-0.3,
            xref="paper",
            yref="paper",
            text=source,
            showarrow=False,
        )
    ],
)

st.plotly_chart(fig, use_container_width=True)
