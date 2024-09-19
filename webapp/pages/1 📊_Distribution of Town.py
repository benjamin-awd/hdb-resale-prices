import numpy as np
import plotly.express as px
import polars as pl
import streamlit as st

from webapp.read import load_dataframe

st.title("📊 Distribution of Resale Price")
st.write(
    "Find out how much you will need approximately for buying a flat in the respective towns."
)
df = load_dataframe()

option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)
filtered = df.filter(pl.col("flat_type") == option_flat)

select_lease = st.selectbox(
    "Select remaining lease years",
    sorted(list(filtered["cat_remaining_lease_years"].unique())),
)
filtered = filtered.filter(pl.col("cat_remaining_lease_years") == select_lease)

# Generate a rainbow color palette
towns = filtered["town"].unique()
colors = ["hsl({}, 70%, 70%)".format(h) for h in np.linspace(0, 360, len(towns))]

fig = px.strip(
    filtered,
    x="resale_price",
    y="town",
    color="town",
    color_discrete_sequence=colors,
    title="Distribution of Resale Prices by Town",
    labels={"resale_price": "Resale Price", "town": "Town"},
)

fig.update_layout(xaxis_title="Resale Price", yaxis_title="Town", height=900)
fig.update_traces(
    hovertemplate="<b>%{y}</b><br>Resale Price: %{x}<br>",
)

fig.update_layout(hovermode="closest")

st.plotly_chart(fig, use_container_width=True)
