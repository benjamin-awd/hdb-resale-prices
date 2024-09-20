import polars as pl
import streamlit as st


class SidebarFilter:
    def __init__(self, min_date, max_date, df: pl.DataFrame):
        self.min_date = min_date
        self.max_date = max_date
        self.df = df
        self.selected_towns = []

        self.hide_elements()
        self.start_date, self.end_date = self.create_slider()
        self.option_flat = self.create_selectbox()
        self.selected_flat_type = self.filter_by_flat_type()
        self.selected_towns = self.create_multiselect()

    def hide_elements(self):
        hide_css = """
            <style>
                div[data-testid="stSliderTickBarMin"],
                div[data-testid="stSliderTickBarMax"] {
                    display: none;
                }
            </style>
        """
        with st.sidebar:
            st.markdown(hide_css, unsafe_allow_html=True)

    def create_slider(self):
        return st.sidebar.slider(
            "Select Date Range",
            min_value=self.min_date,
            max_value=self.max_date,
            value=(self.min_date, self.max_date),
            format="YYYY-MM",
        )

    def create_selectbox(self):
        flat_types = sorted(self.df["flat_type"].unique())
        flat_types.insert(0, "ALL")
        return st.sidebar.selectbox("Select flat type", flat_types)

    def filter_by_flat_type(self):
        if self.option_flat != "ALL":
            return self.df.filter(pl.col("flat_type") == self.option_flat)
        else:
            return self.df

    def create_multiselect(self):
        town_filter = sorted(self.selected_flat_type["town"].unique())
        return st.sidebar.multiselect(
            "Select town",
            options=town_filter,
            default=None,
            placeholder="Choose town (default: all)",
        )
