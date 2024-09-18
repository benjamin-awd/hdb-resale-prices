import plotly.express as px
import polars as pl
import streamlit as st

from webapp.read import get_dataframe

st.title("📈 Median Resale Prices")

df = get_dataframe()

df = df.with_columns(pl.col("month").str.strptime(pl.Date, "%Y-%m"))

min_date = df["month"].min()
max_date = df["month"].max()

start_date, end_date = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM",
)

flat_types = sorted(df["flat_type"].unique())
flat_types.insert(0, "ALL")
option_flat = st.selectbox("Select flat type", flat_types)

if option_flat != "ALL":
    data_flat = df.filter(pl.col("flat_type") == option_flat)
else:
    data_flat = df

town_filter = sorted(data_flat["town"].unique())
container = st.container()

selected_towns = container.multiselect(
    "Select town",
    options=town_filter,
    default=None,
    placeholder="Choose an option (default: all)",
)

if selected_towns:
    filtered = data_flat.filter(pl.col("town").is_in(selected_towns))
else:
    filtered = data_flat

filtered_df = filtered.filter(
    (pl.col("month") >= start_date) & (pl.col("month") <= end_date)
)

chart_df = (
    filtered_df.group_by(["month", "cat_remaining_lease_years"])
    .agg(pl.median("resale_price").alias("median_resale_price"))
    .sort(["cat_remaining_lease_years", "month"])
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
)

fig = px.line(
    chart_df,
    x="month",
    y="percentage_change",
    color="cat_remaining_lease_years",
    title="Percentage Change in Median Resale Price Over Time",
    labels={
        "percentage_change": "Percentage Change (%)",
        "month": "Month",
        "cat_remaining_lease_years": "Remaining Lease Years",
    },
)

fig.update_xaxes(tickformat="%Y-%m")
fig.update_traces(hovertemplate="%{y:.2f}%")
fig.update_layout(hovermode="x unified")

st.plotly_chart(fig, use_container_width=True)
