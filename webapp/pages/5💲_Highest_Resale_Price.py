import altair as alt
import folium
import polars as pl
import streamlit as st
from streamlit_folium import st_folium

from webapp.read import load_dataframe

st.title("💲Highest Resale Price")
st.write(
    "The unit with the highest resale price per town by flat type is plotted below."
)
st.write(
    "The colour of the pins reflect whether the unit is below or above the median value. Red indicates below median while green indicates above median"
)

# read data
df = load_dataframe()
# get highest price flat by town
highest_price = df.filter(
    pl.col("resale_price") == pl.col("resale_price").max().over(["town", "flat_type"])
)

# flat type data
option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)

# filter to get data from chosen flat type
highest_price_filtered = highest_price.filter(pl.col("flat_type") == option_flat)

####################
### MAP PLOTTING ###
####################
# categorise pin color
median_price = highest_price_filtered["resale_price"].median()
st.write("Median value is ", median_price)
highest_price_filtered = highest_price_filtered.with_columns(
    pl.when(pl.col("resale_price") > median_price)
    .then(pl.lit("Above"))
    .otherwise(pl.lit("Below"))
    .alias("median_category")
)
# plot map
latitude = 1.3521
longitude = 103.8198

sg_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=12,
    attr="OneMap",
)
for lat, lon, address, town, price, lease, level in zip(
    highest_price_filtered["latitude"],
    highest_price_filtered["longitude"],
    highest_price_filtered["address"],
    highest_price_filtered["town"],
    highest_price_filtered["resale_price"],
    highest_price_filtered["remaining_lease_years"],
    highest_price_filtered["storey_range"],
):
    price_rounded = "$" + str(round(price))
    # pin colour
    if price > median_price:
        color = "red"
    else:
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
    folium.Marker(
        [lat, lon], popup=popup, icon=folium.Icon(color=color, icon="home", prefix="fa")
    ).add_to(sg_map)

sw = (
    highest_price_filtered.select([pl.col("latitude").min(), pl.col("longitude").min()])
    .to_numpy()
    .flatten()
    .tolist()
)

ne = (
    highest_price_filtered.select([pl.col("latitude").max(), pl.col("longitude").max()])
    .to_numpy()
    .flatten()
    .tolist()
)

sg_map.fit_bounds([sw, ne])

st_data = st_folium(sg_map, width=1000)

##########################
### BAR CHART PLOTTING ###
##########################
colors = ["#d53e2a", "#71af26"]
domain = ["Above", "Below"]
chart = (
    alt.Chart(highest_price_filtered)
    .mark_bar()
    .encode(
        alt.X("resale_price:Q", axis=alt.Axis(format="", title="Highest Resale Price")),
        alt.Y("town:O", sort="-x", axis=alt.Axis(format="", title="Town")),
        alt.Color(
            "median_category:O",
            scale=alt.Scale(domain=domain, range=colors),
            legend=alt.Legend(title="Median Category"),
        ),
        alt.Tooltip(["town", "resale_price"]),
    )
    .interactive()
)

rule = (
    alt.Chart(highest_price_filtered)
    .mark_rule(color="red")
    .encode(x="median(resale_price):Q")
)

st.altair_chart(chart + rule, use_container_width=True)
