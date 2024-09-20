import folium
import polars as pl
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium

from webapp.read import load_dataframe

st.title("🔍 Town Analysis")

st.write("Look for your potential units by using the filters here!")
#################
### READ DATA ###
#################
df = load_dataframe()

##################
### SELECTIONS ###
##################
# filter flat type
option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)
data_flat = df.filter(pl.col("flat_type") == option_flat)

# filter town
town_filter = list(data_flat["town"].unique())
option_town = st.selectbox("Select a town", options=sorted(town_filter, key=str.lower))
filtered = df.filter(
    (pl.col("town") == option_town) & (pl.col("flat_type") == option_flat)
)

filtered = filtered.with_columns(
    pl.col("resale_price")
    .qcut(3, labels=["Low", "Medium", "High"])
    .alias("cat_resale_price")
)

# Count the occurrences of each bin
cat_resale_price = df.group_by("resale_price").agg(pl.len().alias("count"))
cat_resale_price = cat_resale_price.rename({"resale_price": "Resale Price"})

cat_resale_price = cat_resale_price.with_columns(
    pl.col("Resale Price").cast(pl.Utf8).str.strip_chars("()[]").replace(",", " to")
)

select_lease = st.selectbox(
    "Select remaining lease years",
    sorted(list(filtered["cat_remaining_lease_years"].unique())),
)

filtered = filtered.filter(pl.col("cat_remaining_lease_years") == select_lease)

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
filtered_sub = filtered.filter(
    (pl.col("resale_price") >= select_range[0])
    & (pl.col("resale_price") <= select_range[1])
)

# st.write("**Low (<40th percentile):**", cat_resale_price['Resale Price'][0])
# st.write("**Medium (40th to 60th percentile):**", cat_resale_price['Resale Price'][1])
# st.write("**High (>60th percentile):**", cat_resale_price['Resale Price'][2])
# plot map
latitude = 1.3521
longitude = 103.8198

sg_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=2,
    attr="OpenStreetMap",
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

    html = f"""
        <div style="font-family: 'Source Sans Pro', sans-serif; line-height: 1.5; padding: 3px;">
            <b style="font-size: 16px; color: black;">{address}</b>
            <p style="margin: 10px 0; font-size: 14px; color: black;">
                <span style="font-weight: bold;">Storey:</span> {level}<br>
                <span style="font-weight: bold;">Price:</span> <span style="color: black;">${round(price):,}</span><br>
                <span style="font-weight: bold;">Remaining Lease:</span> {lease} years
            </p>
        </div>
    """

    popup = folium.Popup(html, max_width=170)
    folium.Marker(
        [lat, lon],
        popup=popup,
        icon=folium.Icon(color=color, icon="home", prefix="fa"),
        tooltip=html,
    ).add_to(sg_map)

sw = (
    filtered.select([pl.col("latitude").min(), pl.col("longitude").min()])
    .to_numpy()
    .flatten()
    .tolist()
)

ne = (
    filtered.select([pl.col("latitude").max(), pl.col("longitude").max()])
    .to_numpy()
    .flatten()
    .tolist()
)

sg_map.fit_bounds([sw, ne])

image = Image.open("assets/resale_price_legends.png")

st.image(image)

st_data = st_folium(sg_map, width=1000, use_container_width=True)


########################
###  DOWNLOAD DATA  ####
########################
def convert_df(df: pl.DataFrame):
    return df.write_csv().encode("utf-8")


csv = convert_df(filtered_sub)
st.download_button(
    "Download Filtered Data", csv, "filtered_data.csv", "text/csv", key="download-csv"
)
