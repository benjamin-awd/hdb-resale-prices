import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st

from webapp.filter import SidebarFilter
from webapp.read import load_dataframe

st.set_page_config(layout="wide")

st.title("📈 Price Trend")
st.write("The resale price is aggregated using the median value of each town.")

df = load_dataframe()
sf = SidebarFilter(
    df,
    default_flat_type="4 ROOM",
    default_town="ANG MO KIO",
    select_towns=(True, "multi"),
)

#######################
### PLOT LINE CHART ###
#######################

median_df = (
    sf.df.group_by(["month", "town"])
    .agg(pl.median("resale_price"))
    .sort(["town", "month"])
)
fig = px.line(median_df, x="month", y="resale_price", color="town")

fig.update_xaxes(tickformat="%Y-%m")

fig.update_layout(
    title="Resale Price by Month and Town",
    xaxis_title="Month",
    yaxis_title="Resale Price",
)
fig.update_traces(
    line_shape="spline",
    hovertemplate="<b>%{x}</b><br>Median Resale Price: %{y}<br>",
)

st.plotly_chart(fig, use_container_width=True)
