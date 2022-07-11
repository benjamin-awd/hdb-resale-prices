import pandas as pd
import streamlit as st
from PIL import Image

data = pd.read_csv("data.csv", index_col=0)
earliest_date = min(data["month"])
latest_date = max(data["month"])
range_date = earliest_date + " to " + latest_date

st.title("👋 Welcome!")

st.markdown("The goal of this web application is to assist users in finding a suitable HDB resale flat in Singapore.")
st.write("The data used in the analysis is from ", range_date)
st.markdown("The data is obtained from [data.gov.sg](https://data.gov.sg/) and [OneMap](https://www.onemap.gov.sg/docs/) via their API.")
st.markdown("Explore the different categories of analysis using the sidebar!")

image = Image.open('assets/logo.png')
st.image(image)

