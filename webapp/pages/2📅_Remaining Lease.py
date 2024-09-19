import altair as alt
import polars as pl
import streamlit as st

from webapp.read import load_dataframe

st.title("📅 Remaining Lease")

st.write(
    "Find out the relationship of resale prices and remaining lease years in the various towns and flat type"
)
df = load_dataframe()

option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)

filtered = df.filter(pl.col("flat_type") == option_flat)

town_filter = list(df["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))

filtered = filtered.filter(pl.col("town") == option_town)

####################
### SCATTER PLOT ###
####################

brush = alt.selection_interval()
points = (
    alt.Chart(filtered)
    .mark_point()
    .encode(
        x="remaining_lease_years:Q",
        y="resale_price:Q",
        tooltip=["remaining_lease_years", "resale_price"],
        color=alt.condition(
            brush, "cat_remaining_lease_years:N", alt.value("lightgray")
        ),
    )
    .add_params(brush)
    .interactive()
)

bars = (
    alt.Chart(filtered)
    .mark_bar()
    .encode(
        y="cat_remaining_lease_years:N",
        color="cat_remaining_lease_years:N",
        x="count(cat_remaining_lease_years):Q",
        tooltip=["cat_remaining_lease_years", "count(cat_remaining_lease_years)"],
    )
    .transform_filter(brush)
    .interactive()
)

st.altair_chart(points & bars, use_container_width=True)
