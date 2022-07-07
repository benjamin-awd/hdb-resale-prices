import pandas as pd
import streamlit as st

st.title("Overview")

data = pd.read_csv("data.csv", index_col=0)
