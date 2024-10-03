import polars as pl
import streamlit as st
from dateutil.relativedelta import relativedelta

from webapp.read import load_dataframe


class SidebarFilter:
    def __init__(
        self,
        df: pl.DataFrame = load_dataframe(),
        min_date=None,
        max_date=None,
        select_flat_type=True,
        select_towns=(True, "single"),
        select_lease_years=True,
        default_flat_type="ALL",
        default_town=None,
    ):
        self.df = df
        self.min_date = min_date or self.df["month"].max() - relativedelta(months=12)
        self.max_date = max_date or self.df["month"].max()
        self.selected_towns = []
        self.default_flat_type = default_flat_type
        self.default_town = default_town

        self.hide_elements()

        self.start_date, self.end_date = self.create_slider()
        self.df = self.df.filter(
            (pl.col("month") >= self.start_date) & (pl.col("month") <= self.end_date)
        )

        if select_flat_type:
            self.option_flat = self.create_flat_select()
            self.df = self.filter_by_flat_type()

        show_town_filter, town_filter_type = select_towns
        if show_town_filter:
            if town_filter_type == "single":
                self.selected_towns = self.create_town_select()

            if town_filter_type == "multi":
                self.selected_towns = self.create_town_multiselect()

        if self.selected_towns:
            self.df = self.df.filter(pl.col("town").is_in(self.selected_towns))

        if select_lease_years:
            start_year, end_year = self.create_lease_select()
            self.df = self.df.filter(
                (pl.col("remaining_lease_years") >= start_year)
                & (pl.col("remaining_lease_years") <= end_year)
            )

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
            min_value=self.df["month"].min(),
            max_value=self.df["month"].max(),
            value=(self.min_date, self.max_date),
            format="YYYY-MM",
        )

    def create_flat_select(self):
        flat_types = sorted(self.df["flat_type"].unique())
        flat_types.insert(0, "ALL")
        return st.sidebar.selectbox(
            "Select flat type",
            flat_types,
            index=flat_types.index(self.default_flat_type),
        )

    def filter_by_flat_type(self):
        if self.option_flat != "ALL":
            return self.df.filter(pl.col("flat_type") == self.option_flat)
        else:
            return self.df

    def create_town_select(self):
        town_filter = sorted(self.df["town"].unique())
        if self.default_town in town_filter:
            default_index = town_filter.index(self.default_town)
        else:
            default_index = 0
        town = st.sidebar.selectbox(
            "Select town",
            options=town_filter,
            index=default_index,
            placeholder="Choose town (default: all)",
        )
        return [town]

    def create_town_multiselect(self):
        town_filter = sorted(self.df["town"].unique())
        return st.sidebar.multiselect(
            "Select town(s)",
            options=town_filter,
            default=(
                [self.default_town] if self.default_town else None
            ),  # Use default town for multi-select
            placeholder="Choose town (default: all)",
        )

    def create_lease_select(self):
        return st.sidebar.slider(
            "Select remaining lease years",
            min_value=self.df["remaining_lease_years"].min(),
            max_value=self.df["remaining_lease_years"].max(),
            value=(81, 99),
        )
