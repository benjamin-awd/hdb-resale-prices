import altair as alt
import pandas as pd
import streamlit as st

from webapp.read import get_dataframe

st.title("📊 Distribution of Resale Price")
st.write(
    "Find out how much you will need approximately for buying a flat in the respective towns."
)
# read data
data = get_dataframe()
data = data.drop_duplicates().reset_index().drop("index", axis=1)
data["remaining_lease_years"] = data["remaining_lease"].apply(
    lambda x: int(x.split("years")[0])
)

# flat type data
option_flat = st.selectbox(
    "Select a flat type",
    ("2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"),
)
filtered = data[data["flat_type"] == option_flat]


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


filtered_groupby = filtered.groupby(["town"])["resale_price"].median().reset_index()
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
