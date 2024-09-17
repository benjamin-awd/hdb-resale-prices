import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium

from webapp.read import get_dataframe

st.title("🔍 Town Analysis")

st.write("Look for your potential units by using the filters here!")
#################
### READ DATA ###
#################
data = get_dataframe()
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(
    lambda x: int(x.split("years")[0])
)

##################
### SELECTIONS ###
##################
# filter flat type
option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)
data_flat = data[data["flat_type"] == option_flat]

# filter town
town_filter = list(data_flat["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))
filtered = data_flat[data_flat["town"] == option_town]

# create category for resale price
labels = ["Low", "Medium", "High"]

filtered["cat_resale_price"] = pd.qcut(
    filtered["resale_price"], [0, 0.4, 0.6, 1], labels=labels
)
cat_resale_price = pd.DataFrame(
    pd.qcut(filtered["resale_price"], [0, 0.4, 0.6, 1]).value_counts().reset_index()
)
cat_resale_price["index"] = cat_resale_price.index.astype(str)
cat_resale_price = (
    cat_resale_price.sort_values("index", ascending=True)
    .reset_index()
    .drop(["level_0", "resale_price"], axis=1)
)
cat_resale_price = cat_resale_price.rename(columns={"index": "Resale Price"})
cat_resale_price["Resale Price"] = cat_resale_price["Resale Price"].apply(
    lambda x: x.strip("()[]")
)
cat_resale_price["Resale Price"] = cat_resale_price["Resale Price"].apply(
    lambda x: x.replace(",", " to")
)


# set remaining lease
def convert_lease(x):
    if 0 < x <= 60:
        result = "0-60 years"
    elif 60 < x <= 80:
        result = "61-80 years"
    elif 80 < x <= 99:
        result = "81-99 years"
    return result


filtered["cat_remaining_lease_years"] = filtered["remaining_lease_years"].apply(
    convert_lease
)
select_lease = st.selectbox(
    "Select remaining lease years",
    sorted(list(filtered["cat_remaining_lease_years"].unique())),
)

filtered = filtered[filtered["cat_remaining_lease_years"] == select_lease]

# set slider range for resale price
min_value = int(filtered["resale_price"].min())
max_value = int(filtered["resale_price"].max())

select_range = st.slider(
    "Select resale price range ($)",
    min_value,
    max_value,
    (min_value, max_value),
    step=10000,
)


####################
### MAP PLOTTING ###
####################
# filter selection according to range
filtered_sub = filtered[
    (filtered["resale_price"] >= select_range[0])
    & (filtered["resale_price"] <= select_range[1])
]

# st.write("**Low (<40th percentile):**", cat_resale_price['Resale Price'][0])
# st.write("**Medium (40th to 60th percentile):**", cat_resale_price['Resale Price'][1])
# st.write("**High (>60th percentile):**", cat_resale_price['Resale Price'][2])
# plot map
latitude = 1.3521
longitude = 103.8198

sg_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=2,
    attr="OneMap",
)
for lat, lon, address, town, price, lease, level, cat_resale_price in zip(
    filtered_sub["latitude"],
    filtered_sub["longitude"],
    filtered_sub["address"],
    filtered_sub["town"],
    filtered_sub["resale_price"],
    filtered_sub["remaining_lease_years"],
    filtered_sub["storey_range"],
    filtered_sub["cat_resale_price"],
):
    price_rounded = "$" + str(round(price))
    # pin colour
    if cat_resale_price == "Low":
        color = "green"
    elif cat_resale_price == "Medium":
        color = "orange"
    elif cat_resale_price == "High":
        color = "red"

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
    folium.Marker(
        [lat, lon], popup=popup, icon=folium.Icon(color=color, icon="home", prefix="fa")
    ).add_to(sg_map)

sw = filtered[["latitude", "longitude"]].min().values.tolist()
ne = filtered[["latitude", "longitude"]].max().values.tolist()

sg_map.fit_bounds([sw, ne])

image = Image.open("assets/resale_price_legends.png")

st.image(image)

st_data = st_folium(sg_map, width=1000)


########################
###  DOWNLOAD DATA  ####
########################
@st.cache
def convert_df(df):
    return df.to_csv().encode("utf-8")


csv = convert_df(filtered_sub)
st.download_button(
    "Download Filtered Data", csv, "filtered_data.csv", "text/csv", key="download-csv"
)
