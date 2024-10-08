import plotly.express as px
import streamlit as st

from webapp.filter import SidebarFilter

st.set_page_config(layout="wide")

st.title("📅 Remaining Lease")

st.write(
    "Find out the relationship of resale prices and remaining lease years in the various towns and flat type"
)
sf = SidebarFilter(select_lease_years=False, default_flat_type="4 ROOM")

scatter_fig = px.scatter(
    sf.df.sort(by="cat_remaining_lease_years"),
    x="remaining_lease_years",
    y="resale_price",
    color="cat_remaining_lease_years",
    hover_data=[
        "remaining_lease_years",
        "resale_price",
        "address",
        "storey_range",
        "month",
    ],
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
    hovertemplate="<b>Price:</b> $%{y:,.3s}<br>"
    + "<b>Lease Years:</b> %{x} years<br>"
    + "<b>Address:</b> %{customdata[0]}<br>"
    + "<b>Storey:</b> %{customdata[1]}<br>"
    + "<b>Sold:</b> %{customdata[2]|%Y-%m}<br>",
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
    text="len",
)

scatter_fig.update_layout(height=600)
bar_fig.update_layout(height=250)
bar_fig.update_traces(textposition="outside", selector=dict(type="bar"))


st.plotly_chart(scatter_fig, use_container_width=True)
st.plotly_chart(bar_fig, use_container_width=True)
