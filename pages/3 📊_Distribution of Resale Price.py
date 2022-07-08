import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import altair as alt

st.title("📊 Distribution of Resale Price")


# read data
data = pd.read_csv("data.csv", index_col=0)
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(lambda x: x.split("years")[0])

# flat type data
option_flat = st.selectbox("Select a flat type", 
             ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"))

filtered = data[data["flat_type"] == option_flat]

boxplot = alt.Chart(filtered).mark_boxplot(extent='min-max').encode(
    x='town:O',
    y='resale_price:Q'
).properties(
    height=500
)

st.altair_chart(boxplot, use_container_width=True)