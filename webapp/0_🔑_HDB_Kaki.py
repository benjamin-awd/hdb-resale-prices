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

st.markdown(
    "HDB Kaki helps you stay updated on the latest movements in the HDB resale market."
)

df = load_dataframe()


def add_time_filters(df: pl.DataFrame):
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


group_by = st.radio(
    "Group by:",
    ("Lease Years", "Town"),
)

source = "Source: <a href='https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view'>data.gov.sg</a>"

annotations = dict(
    margin=dict(l=50, r=50, t=100, b=100),
    annotations=[
        dict(
            x=0.5,
            y=-0.33,
            xref="paper",
            yref="paper",
            text=source,
            showarrow=False,
        )
    ],
    height=500,
)

if group_by == "Lease Years":
    sf = SidebarFilter(
        df,
        min_date=datetime.strptime("2017-01-01", "%Y-%m-%d").date(),
        select_towns=(True, "multi"),
        select_lease_years=False,
    )

    chart_df = add_time_filters(sf.df)
    chart_df = (
        chart_df.group_by(["quarter_label", "cat_remaining_lease_years"])
        .agg(pl.median("resale_price").alias("median_resale_price"))
        .sort(["cat_remaining_lease_years", "quarter_label"])
    )
    chart_df = chart_df.with_columns(
        (
            (
                pl.col("median_resale_price")
                / pl.first("median_resale_price").over("cat_remaining_lease_years")
                - 1
            )
            * 100
        ).alias("percentage_change")
    ).sort(by="quarter_label")

    fig = px.line(
        chart_df,
        x="quarter_label",
        y="percentage_change",
        color="cat_remaining_lease_years",
        title=f"Percentage Change in Median Resale Price since {str(sf.start_date)[:7]}",
        labels={
            "percentage_change": "Percentage Change (%)",
            "quarter_label": "Quarter",
            "cat_remaining_lease_years": "Remaining Lease Years",
        },
    )

    fig.update_yaxes(ticksuffix="%")
    fig.update_traces(hovertemplate="%{y:.2f}%")

    fig.update_layout(hovermode="x unified", **annotations)
    st.plotly_chart(fig, use_container_width=True)

else:
    sf = SidebarFilter(
        df,
        min_date=df["month"].min(),
        select_towns=(True, "multi"),
        select_lease_years=False,
        default_town="ANG MO KIO",
    )

    chart_df = add_time_filters(sf.df)

    chart_df = (
        chart_df.group_by(["quarter_label", "town"])
        .agg(pl.median("resale_price").alias("resale_price"))
        .sort(["town", "quarter_label"])
    ).sort(by="quarter_label")

    # Plot for months and towns
    fig = px.line(
        chart_df,
        x="quarter_label",
        y="resale_price",
        color="town",
        labels={"town": "Town"},
    )

    fig.update_xaxes(tickformat="%Y-%m")
    fig.update_layout(
        title="Median Resale Price by Town",
        xaxis_title="Quarter",
        yaxis_title="Resale Price",
        hovermode="x unified",
        **annotations,
    )
    fig.update_traces(
        line_shape="spline",
        hovertemplate="$%{y}",
    )

    st.plotly_chart(fig, use_container_width=True)
