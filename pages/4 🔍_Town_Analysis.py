import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import altair as alt
from PIL import Image


st.title("🔍 Town Analysis")

#################
### READ DATA ###
#################
data = pd.read_csv("data.csv", index_col=0)
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(lambda x: int(x.split("years")[0]))

##################
### SELECTIONS ###
##################
# filter flat type
option_flat = st.selectbox("Select a flat type", 
             ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"))
data_flat = data[data["flat_type"] == option_flat]

# filter town 
town_filter = list(data_flat["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))
filtered = data_flat[data_flat["town"] == option_town]

# set slider range for resale price
min_value = int(filtered["resale_price"].min())
max_value = int(filtered["resale_price"].max())

select_range = st.slider("Select resale price range", 
                 min_value, max_value, (min_value, max_value), step=10000)

# set map view

select_map_view = st.radio("Select map view", ["Resale Price", "Remaining Lease"])

#######################
### CREATE FEATURES ###
#######################
# create category for resale price
labels = ['0-25%', '25-50%', '50-75%', '75-100%']
filtered["cat_resale_price"] = pd.qcut(filtered["resale_price"], q=4, labels=labels)

# create category for remaining lease
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
### MAP PLOTTING ###
####################
# filter selection according to range
filtered_sub = filtered[(filtered["resale_price"] >= select_range[0]) & (filtered["resale_price"] <= select_range[1])]

# plot map
latitude = 1.3521
longitude = 103.8198

sg_map = folium.Map(location=[latitude, longitude], zoom_start=2, tiles="Open Street Map")
for lat, lon, address, town, price, lease, level, cat_resale_price, cat_remain_lease in zip(filtered_sub["latitude"], filtered_sub["longitude"], filtered_sub["address"], filtered_sub["town"], filtered_sub["resale_price"], filtered_sub["remaining_lease_years"], filtered_sub["storey_range"], filtered_sub["cat_resale_price"], filtered_sub["cat_remaining_lease_years"]):
    price_rounded = "$" + str(round(price))
    
    if select_map_view == "Resale Price":
        # pin colour
        if cat_resale_price == "0-25%":
            color = "lightblue"
        elif cat_resale_price == "25-50%":
            color = "blue"
        elif cat_resale_price == "50-75%":
            color = "darkblue"
        elif cat_resale_price == "75-100%":
            color = "cadetblue"
            
    elif select_map_view == "Remaining Lease":
        # pin colour
        if cat_remain_lease == "0-60":
            color = "red"
        elif cat_remain_lease == "61-80":
            color = "orange"
        elif cat_remain_lease == "81-99":
            color = "green"
            
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

if (select_map_view == "Resale Price"):
    image = Image.open('assets/resale_map_legends.png')
elif (select_map_view == "Remaining Lease"):
    image = Image.open('assets/remaining_lease_map_legends.png')
st.image(image)

st_data = st_folium(sg_map, width=1000)
