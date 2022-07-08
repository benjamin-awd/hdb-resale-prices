import pandas as pd
import streamlit as st
import altair as alt
from streamlit_folium import st_folium
import folium

st.title("Remaining Lease")

data = pd.read_csv("data.csv", index_col=0)
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(lambda x: float(x.split("years")[0]))

option_flat = st.selectbox("Select a flat type", 
             ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"))

data_flat = data[data["flat_type"] == option_flat]

town_filter = list(data_flat["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))

filtered = data_flat[data_flat["town"] == option_town]


def convert_lease(x):
    if (0<x<=60):
        result = "0-60"
    elif (60<x<=80):
        result = "61-80"
    elif (80<x<=99):
        result = "81-99"
    return result

filtered["cat_remaining_lease_years"] = filtered["remaining_lease_years"].apply(convert_lease)


####################
### SCATTER PLOT ###
####################

brush = alt.selection(type='interval')
points = alt.Chart(filtered).mark_point().encode(
    x='remaining_lease_years:Q',
    y='resale_price:Q',
    tooltip=["remaining_lease_years", "resale_price"],
    color=alt.condition(brush, 'cat_remaining_lease_years:N', alt.value('lightgray'))
).add_selection(
    brush
).interactive()

bars = alt.Chart(filtered).mark_bar().encode(
    y='cat_remaining_lease_years:N',
    color='cat_remaining_lease_years:N',
    x='count(cat_remaining_lease_years):Q',
    tooltip=["cat_remaining_lease_years", "count(cat_remaining_lease_years)"],
).transform_filter(
    brush
).interactive()

st.altair_chart(points & bars, use_container_width=True)

