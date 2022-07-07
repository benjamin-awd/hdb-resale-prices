import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt


st.title("Town Analysis")
st.write("There are four shades of blue pins in the map below - lightblue, blue, cadetblue, darkblue")
st.write("They represent 0-25th, 25-50th, 50-75th and 75-100th percentile respectively. In other words, the darker the colour of the pins, the higher the resale price.")
data = pd.read_csv("data.csv", index_col=0)
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(lambda x: x.split("years")[0])

option_flat = st.selectbox("Select a flat type", 
             ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"))

data_flat = data[data["flat_type"] == option_flat]
town_filter = list(data_flat["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))

filtered = data_flat[data_flat["town"] == option_town]

####################
### MAP PLOTTING ###
####################
# categorise pin color
labels = ['0-25%', '25-50%', '50-75%', '75-100%']
filtered["cat_resale_price"] = pd.qcut(filtered["resale_price"], q=4, labels=labels)

# plot map
latitude = 1.3521
longitude = 103.8198

sg_map = folium.Map(location=[latitude, longitude], zoom_start=2, tiles="Open Street Map")
for lat, lon, address, town, price, lease, level, cat in zip(filtered["latitude"], filtered["longitude"], filtered["address"], filtered["town"], filtered["resale_price"], filtered["remaining_lease_years"], filtered["storey_range"], filtered["cat_resale_price"]):
    price_rounded = "$" + str(round(price))
    # pin colour
    if cat == "0-25%":
        color = "lightblue"
    elif cat == "25-50%":
        color = "blue"
    elif cat == "50-75%":
        color = "cadetblue"
    elif cat == "75-100%":
        color = "darkblue"
    
    # html for popup
    html = f"""
            <h4>{town}</h4>
            <b>{address}</b>
            <p>{level} storey
                <br>
                {price_rounded}
                <br>
                {lease} years remaining
            </p>

    """
        
    popup = folium.Popup(html, max_width=170)
    folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color, icon='home', prefix='fa')).add_to(sg_map)
    
sw = filtered[["latitude", "longitude"]].min().values.tolist()
ne = filtered[["latitude", "longitude"]].max().values.tolist()

sg_map.fit_bounds([sw, ne])

st_data = st_folium(sg_map, width=1000)
