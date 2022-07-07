import pandas as pd
import streamlit as st
from PIL import Image

data = pd.read_csv("data.csv", index_col=0)
st.dataframe(data)