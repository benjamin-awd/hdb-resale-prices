import polars as pl
import streamlit as st


class SidebarFilter:
    def __init__(
        self,
        min_date,
        max_date,
        df: pl.DataFrame,
        select_flat_type=True,
        select_towns=(True, "single"),
        remaining_lease_years=True,
    ):
        self.min_date = min_date
        self.max_date = max_date
        self.df = df
        self.selected_towns = []

        self.hide_elements()

        self.start_date, self.end_date = self.create_slider()
        self.df.filter((pl.col("month") >= min_date) & (pl.col("month") <= max_date))

        if select_flat_type:
            self.option_flat = self.create_selectbox()
            self.df = self.filter_by_flat_type()

        show_town_filter, town_filter_type = select_towns
        if show_town_filter:
            if town_filter_type == "single":
                self.selected_towns = self.create_town_select()

            if town_filter_type == "multi":
                self.selected_towns = self.create_town_multiselect()

        if self.selected_towns:
            self.df = self.df.filter(pl.col("town").is_in(self.selected_towns))

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
            "Select date range",
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

    def create_town_select(self):
        town_filter = sorted(self.df["town"].unique())
        town = st.sidebar.selectbox(
            "Select town",
            options=town_filter,
            placeholder="Choose town (default: all)",
        )
        return [town]

    def create_town_multiselect(self):
        town_filter = sorted(self.df["town"].unique())
        return st.sidebar.multiselect(
            "Select town(s)",
            options=town_filter,
            default=None,
            placeholder="Choose town (default: all)",
        )
