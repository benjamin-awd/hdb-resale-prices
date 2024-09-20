import folium
import plotly.express as px
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

highest_price_filtered = highest_price.filter(pl.col("flat_type") == option_flat)

highest_price_per_town = highest_price_filtered.group_by("town").agg(
    pl.max("resale_price").alias("max_resale_price")
)

highest_price_per_town = highest_price_filtered.join(
    highest_price_per_town,
    left_on=["town", "resale_price"],
    right_on=["town", "max_resale_price"],
    how="inner",
)

highest_price_per_town = highest_price_per_town.unique(subset=["town", "resale_price"])
highest_price_per_town = highest_price_per_town.sort("resale_price")

####################
### MAP PLOTTING ###
####################
# categorise pin color
median_price = highest_price_per_town["resale_price"].median()
highest_price_per_town = highest_price_per_town.with_columns(
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
    attr="OpenStreetMap",
)
for month, lat, lon, address, town, price, lease, level in zip(
    highest_price_filtered["month"],
    highest_price_filtered["latitude"],
    highest_price_filtered["longitude"],
    highest_price_filtered["address"],
    highest_price_filtered["town"],
    highest_price_filtered["resale_price"],
    highest_price_filtered["remaining_lease_years"],
    highest_price_filtered["storey_range"],
):
    # pin colour
    if price > median_price:
        color = "red"
    else:
        color = "green"

    # html for popup
    html = f"""
        <div style="font-family: 'Source Sans Pro', sans-serif; line-height: 1.5; padding: 3px;">
            <b style="font-size: 16px;">{address}</b>
            <p style="margin: 10px 0; font-size: 14px;">
                <span style="font-weight: bold;">Sold:</span> {month}<br>
                <span style="font-weight: bold;">Storey:</span> {level}<br>
                <span style="font-weight: bold;">Price:</span> ${round(price):,}</span><br>
                <span style="font-weight: bold;">Remaining Lease:</span> {lease} years
            </p>
        </div>
    """

    popup = folium.Popup(html, max_width=170)
    folium.Marker(
        [lat, lon],
        popup=popup,
        tooltip=html,
        icon=folium.Icon(color=color, icon="home", prefix="fa"),
    ).add_to(sg_map)

sw = (
    highest_price_per_town.select([pl.col("latitude").min(), pl.col("longitude").min()])
    .to_numpy()
    .flatten()
    .tolist()
)

ne = (
    highest_price_per_town.select([pl.col("latitude").max(), pl.col("longitude").max()])
    .to_numpy()
    .flatten()
    .tolist()
)

sg_map.fit_bounds([sw, ne])

st_data = st_folium(sg_map, width=1000)

##########################
### BAR CHART PLOTTING ###
##########################
fig = px.bar(
    highest_price_per_town.sort(by="resale_price"),
    x="resale_price",
    y="town",
    color="median_category",
    color_discrete_map={"Below": "#71af26", "Above": "#d53e2a"},
    labels={"resale_price": "Highest Resale Price", "town": "Town"},
    title="Highest Resale Price per Town",
)

fig.add_shape(
    type="line",
    x0=median_price,
    y0=-0.5,
    x1=median_price,
    y1=len(highest_price_filtered) - 0.5,
    line=dict(color="dark gray", width=2, dash="dash"),
)

# Update layout
fig.update_layout(
    yaxis_title="Town",
    xaxis_title=f"Highest Resale Price (median: ${round(median_price/1000):,.0f}K)",
    height=700,
)

st.plotly_chart(fig)
