import altair as alt
import streamlit as st

from webapp.filter import SidebarFilter
from webapp.read import load_dataframe

st.set_page_config(layout="wide")

st.title("📅 Remaining Lease")

st.write(
    "Find out the relationship of resale prices and remaining lease years in the various towns and flat type"
)
df = load_dataframe()
sf = SidebarFilter(df, select_lease_years=False, default_flat_type="4 ROOM")

brush = alt.selection_interval()
points = (
    alt.Chart(sf.df)
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
    alt.Chart(sf.df)
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
