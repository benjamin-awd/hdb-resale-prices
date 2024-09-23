import plotly.express as px
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

scatter_fig = px.scatter(
    sf.df,
    x="remaining_lease_years",
    y="resale_price",
    color="cat_remaining_lease_years",
    hover_data=["remaining_lease_years", "resale_price"],
    labels={
        "remaining_lease_years": "Remaining Lease Years",
        "resale_price": "Resale Price",
        "cat_remaining_lease_years": "Remaining Lease Category",
    },
)

scatter_fig.update_traces(
    marker=dict(
        size=6,
        symbol="circle-open",
        opacity=1,
        line=dict(width=1.5),
    ),
    selector=dict(mode="markers"),
)

bar_fig = px.bar(
    sf.df.group_by("cat_remaining_lease_years")
    .len()
    .sort(by="cat_remaining_lease_years"),
    x="len",
    y="cat_remaining_lease_years",
    color="cat_remaining_lease_years",
    orientation="h",
    labels={"cat_remaining_lease_years": "Remaining Lease Category", "len": "Count"},
)

scatter_fig.update_layout(height=600)
bar_fig.update_layout(height=250)

st.plotly_chart(scatter_fig, use_container_width=True)
st.plotly_chart(bar_fig, use_container_width=True)
