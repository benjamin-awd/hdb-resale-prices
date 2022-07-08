import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import altair as alt

st.title("Price Trend")
st.write("The resale price is aggregated using the median value of each town.")

data = pd.read_csv("data.csv", index_col=0)
data = data.drop_duplicates().reset_index().drop("index", axis=1)
option_flat = st.selectbox("Select a flat type", 
             ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"))

data_flat = data[data["flat_type"] == option_flat]
town_filter = list(data_flat["town"].unique())
option_town = st.multiselect("Select multiple towns to compare", options=sorted(town_filter, key=str.lower), default=town_filter[0])

filtered = data_flat[data_flat["town"].isin(option_town)]
town_group = filtered.groupby(["town", "month"])["resale_price"].median().reset_index()
#######################
### PLOT LINE CHART ###
#######################
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['month'], empty='none')

line = alt.Chart(town_group).mark_line(interpolate='basis').encode(
    x='month:O',
    y='resale_price:Q',
    color='town:N'
)
selectors = alt.Chart(town_group).mark_point().encode(
    x='month:O',
    opacity=alt.value(0),
).add_selection(
    nearest
)
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'resale_price:Q', alt.value(' '))
)
rules = alt.Chart(town_group).mark_rule(color='gray').encode(
    x='month:O',
).transform_filter(
    nearest
)

st.altair_chart(alt.layer(line, selectors, points, rules, text), use_container_width=True)