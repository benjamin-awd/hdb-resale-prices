import folium
import polars as pl
import streamlit as st
from folium.plugins import FastMarkerCluster
from PIL import Image
from streamlit_folium import st_folium

from webapp.filter import SidebarFilter

st.set_page_config(layout="wide")

st.title("🔍 Town Analysis")

st.write(
    "To view only the latest transactions within the date range, click on the `Show all transactions` toggle."
)

st.write(
    "Note: The `threshold` parameter determines the price category of the resale. "
    + "A higher `threshold` increases the range for 'Medium' prices and reduces"
    + " the number of items classified as 'Low' or 'High'."
)

# filter flat type
sf = SidebarFilter(
    select_towns=(True, "multi"),
    default_flat_type="4 ROOM",
)

col1, col2 = st.columns(spec=[0.9, 0.2])
percentage_threshold = col2.number_input("Threshold", 0.0, 1.0, 0.1, step=0.1)

show_all = st.sidebar.toggle("Show all transactions", value=True)

try:
    median_resale_price = sf.df["resale_price"].median()
    # Calculate the absolute threshold value based on the percentage
    threshold = median_resale_price * percentage_threshold

    # Bin the resale prices based on the median and percentage threshold
    filtered = sf.df.with_columns(
        pl.when(pl.col("resale_price") < (median_resale_price - threshold))
        .then(pl.lit("Low"))
        .when(pl.col("resale_price") > (median_resale_price + threshold))
        .then(pl.lit("High"))
        .otherwise(pl.lit("Medium"))
        .alias("cat_resale_price")
    )

    st.write(
        f"Median price: `${median_resale_price:,.0f}`",
    )
    # Count the occurrences of each bin
    cat_resale_price = sf.df.group_by("resale_price").agg(pl.len().alias("count"))
    cat_resale_price = cat_resale_price.rename({"resale_price": "Resale Price"})

    cat_resale_price = cat_resale_price.with_columns(
        pl.col("Resale Price").cast(pl.Utf8).str.strip_chars("()[]").replace(",", " to")
    )

    # set slider range for resale price
    min_value = int(filtered["resale_price"].min())
    max_value = int(filtered["resale_price"].max())

    min_select, max_select = col1.slider(
        "Select resale price range ($)",
        int(min_value / 1000),
        int(max_value / 1000),
        (int(min_value / 1000), int(max_value / 1000)),
        step=10,
        format="$%sk",
    )
    ####################
    ### MAP PLOTTING ###
    ####################
    filtered_sub = filtered.filter(
        (pl.col("resale_price") >= min_select * 1000)
        & (pl.col("resale_price") <= max_select * 1000)
    )

    latitude = 1.3521
    longitude = 103.8198

    sg_map = folium.Map(
        location=[latitude, longitude],
        zoom_start=2,
        attr="OpenStreetMap",
        prefer_canvas=True,
    )

    callback = """
        function(row) {
            var lat = row[0];
            var lng = row[1];
            var address = row[2];
            var month = row[3];
            var level = row[4];
            var price = row[5];
            var lease = row[6];
            var cat_resale_price = row[7];

            var color = cat_resale_price === "Low" ? "green" :
                        cat_resale_price === "Medium" ? "orange" : "red";

            var html = `
                <div style="font-family: 'Source Sans Pro', sans-serif; line-height: 1.5; padding: 3px;">
                    <b style="font-size: 16px;">${address}</b>
                    <p style="margin: 10px 0; font-size: 14px;">
                        <span style="font-weight: bold;">Sold:</span> ${month}<br>
                        <span style="font-weight: bold;">Storey:</span> ${level}<br>
                        <span style="font-weight: bold;">Price:</span> $${price.toLocaleString()}<br>
                        <span style="font-weight: bold;">Remaining Lease:</span> ${lease} years
                    </p>
                </div>
            `;

            var icon = L.AwesomeMarkers.icon({
                icon: 'home',
                markerColor: color,
                prefix: 'fa'
            });

            var marker = L.marker(new L.LatLng(lat, lng), {icon: icon});
            marker.bindPopup(html);
            marker.bindTooltip(html, {sticky: true});
            return marker;
        }
    """

    if show_all:
        filtered_data = filtered_sub
    else:
        latest_transactions = filtered_sub.group_by("address").agg(
            pl.all().sort_by("month").last()
        )
        filtered_data = latest_transactions

    filtered_data = filtered_data.with_columns(
        [
            pl.col("month").cast(pl.Utf8),
        ]
    )

    data = (
        filtered_data.select(
            [
                "latitude",
                "longitude",
                "address",
                "month",
                "storey_range",
                "resale_price",
                "remaining_lease_years",
                "cat_resale_price",
            ]
        )
        .to_numpy()
        .tolist()
    )
    marker_cluster = FastMarkerCluster(
        data,
        callback=callback,
        name="Resale Flats",
    ).add_to(sg_map)

    folium.LayerControl().add_to(sg_map)

    folium_object = sg_map
    if show_all:
        folium_object = marker_cluster

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

    st_data = st_folium(sg_map, use_container_width=True, returned_objects=[])

except TypeError as error:
    st.warning(f"No data found for this combination of settings: {error}")


def convert_df(df: pl.DataFrame):
    return df.write_csv().encode("utf-8")


csv = convert_df(filtered_sub)
st.download_button(
    "Download Filtered Data",
    csv,
    "filtered_data.csv",
    "text/csv",
    key="download-csv",
)


simple_df = filtered.select(
    pl.col("month").dt.strftime("%Y-%m").alias("month_sold"),
    "town",
    "flat_type",
    "address",
    "resale_price",
    pl.col("lease_commence_date").cast(str),
    "remaining_lease",
    "cat_resale_price",
)

st.write("")
st.write("Data points as shown on map:")

st.dataframe(simple_df, use_container_width=True)
