import numpy as np
import plotly.express as px
import streamlit as st

from webapp.filter import SidebarFilter

st.set_page_config(layout="wide")

st.title("📊 Distribution of Resale Price")
st.write(
    "Find out how much you will need approximately for buying a flat in the respective towns."
)

sf = SidebarFilter(select_towns=(False, ""), default_flat_type="4 ROOM")

# Generate a rainbow color palette
towns = sf.df["town"].unique()
colors = ["hsl({}, 70%, 70%)".format(h) for h in np.linspace(0, 360, len(towns))]

fig = px.box(
    sf.df,
    x="town",
    y="resale_price",
    color="town",
    color_discrete_sequence=colors,
    title="Distribution of Resale Prices by Town",
    labels={"resale_price": "Resale Price", "town": "Town"},
)

fig.update_layout(
    xaxis_title="Resale Price",
    yaxis_title="Town",
    height=900,
    legend=dict(
        y=-0.55,
        orientation="h",
        yanchor="bottom",
        xanchor="right",
        yref="container",
        x=0.9,
    ),
)
fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Resale Price: %{y}<br>",
)

fig.update_layout(hovermode="closest")

st.plotly_chart(fig, use_container_width=True)
