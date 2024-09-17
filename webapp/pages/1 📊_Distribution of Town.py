import altair as alt
import polars as pl
import streamlit as st

from webapp.read import get_dataframe

st.title("📊 Distribution of Resale Price")
st.write(
    "Find out how much you will need approximately for buying a flat in the respective towns."
)
# read data
df = get_dataframe()

# flat type data
option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)
filtered = df.filter(pl.col("flat_type") == option_flat)


# set remaining lease
select_lease = st.selectbox(
    "Select remaining lease years",
    sorted(list(filtered["cat_remaining_lease_years"].unique())),
)
filtered = filtered.filter(pl.col("cat_remaining_lease_years") == select_lease)
filtered_groupby = filtered.group_by("town").agg(pl.col("resale_price").median())
filtered_groupby_resale_min = round(filtered_groupby["resale_price"].min() - 100000, -4)
filtered_groupny_resale_max = round(filtered_groupby["resale_price"].max() + 100000, -4)

points = (
    alt.Chart(filtered)
    .mark_point(filled=True, size=200)
    .encode(
        x=alt.X(
            "median(resale_price):Q",
            scale=alt.Scale(
                domain=[filtered_groupby_resale_min, filtered_groupny_resale_max]
            ),
        ),
        y=alt.Y("town:O"),
        tooltip=alt.Tooltip(["town", "median(resale_price)"]),
    )
    .properties(height=500)
    .interactive()
)


st.altair_chart(points, use_container_width=True)
