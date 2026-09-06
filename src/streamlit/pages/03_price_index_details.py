""" X """

import streamlit as st
import pandas as pd

from src.config import SUPPORTED_INDEX_LIST, ECONOMY_MASTER_DATA, EVENTS_MASTER_DATA, RETURNS_DATA, SQ_RETURNS_DATA, VOL30_DATA, VOL7_DATA
from src.visualisation.plot_graph import plot_index_price, plot_returns
from src.streamlit.steamlit_helpers import filter_dataframe
from src.streamlit.ui.graph_box import graph_box



#------------------------
# Page Config
#------------------------

SUPPORTED_INDEX_LIST = list(SUPPORTED_INDEX_LIST)

#from previous page
INDEX_NAME = str(st.query_params.get("index"))

if INDEX_NAME is None or INDEX_NAME not in SUPPORTED_INDEX_LIST:
    st.warning(f"No index selected or your submitted index is invalid ({INDEX_NAME}). Please select an index.")

    selected_index = st.selectbox(
        "Select Index",
        options= [None] + SUPPORTED_INDEX_LIST,
        key="index_selector",
        index=0
    )

    if selected_index in SUPPORTED_INDEX_LIST:
        st.query_params["index"] = selected_index
        st.rerun()

st.set_page_config(
    page_title=f"{INDEX_NAME.title()} — Detailed Statistics",
    page_icon="📈",
    layout="wide"
)


#------------------------
# Load Data
#------------------------
ECONOMIC_DATA = pd.read_csv(ECONOMY_MASTER_DATA)
ECONOMIC_DATA["date"] = pd.to_datetime(ECONOMIC_DATA["date"],errors="coerce")

EVENTS_DATA = pd.read_csv(EVENTS_MASTER_DATA)
EVENTS_DATA["date"] = pd.to_datetime(EVENTS_DATA["date"],errors="coerce")

RETURNS_DATA = pd.read_csv(RETURNS_DATA)
RETURNS_DATA["date"] = pd.to_datetime(RETURNS_DATA["date"], errors="coerce")

SQ_DATA = pd.read_csv(SQ_RETURNS_DATA)
SQ_DATA["date"] = pd.to_datetime(SQ_DATA["date"], errors="coerce")

V7_DATA = pd.read_csv(VOL7_DATA)
V7_DATA["date"] = pd.to_datetime(V7_DATA["date"], errors="coerce")

V30_DATA = pd.read_csv(VOL30_DATA)
V30_DATA["date"] = pd.to_datetime(V30_DATA["date"], errors="coerce")

#------------------------
# Title
#------------------------

st.title(f"{INDEX_NAME.title()} — Detailed Statistics")
if INDEX_NAME is None:
    st.write(
        f"""
            Detailed economic statistics for {INDEX_NAME} showing a
            range of metrics and where applicable GARCH analysis if
            data fits the GARCH hypothesis.
        """
    )

#------------------------
# filters
#------------------------

def reset_date_filter():
    st.session_state["date_filter"] = (ECONOMIC_DATA["date"].min().date(), ECONOMIC_DATA["date"].max().date())

min_date = ECONOMIC_DATA["date"].min().date()
max_date = ECONOMIC_DATA["date"].max().date()

if "date_filter" not in st.session_state:
    st.session_state["date_filter"] = (ECONOMIC_DATA["date"].min().date(), ECONOMIC_DATA["date"].max().date())

if INDEX_NAME is not None and INDEX_NAME in SUPPORTED_INDEX_LIST:

    col1, col2 = st.columns([5, 1])

    with col1:
        selected_dates = st.date_input(
            "Date Range",
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )

    with col2:
        st.write("")
        st.write("")

        st.button(
            "Reset",
            use_container_width=True,
            on_click=reset_date_filter
        )

    filtered_economic_data = ECONOMIC_DATA
    filtered_returns_data = RETURNS_DATA
    filtered_v7_data = V7_DATA
    filtered_v30_data = V30_DATA
    filtered_sq_data = SQ_DATA

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_economic_data = filter_dataframe(ECONOMIC_DATA,"date",start_date,end_date)
        filtered_returns_data = filter_dataframe(RETURNS_DATA,"date",start_date,end_date)
        filtered_sq_data = filter_dataframe(SQ_DATA,"date",start_date,end_date)
        filtered_v7_data = filter_dataframe(V7_DATA,"date",start_date,end_date)
        filtered_v30_data = filter_dataframe(V30_DATA,"date",start_date,end_date)

    min_date = filtered_economic_data["date"].min().date()
    max_date = filtered_economic_data["date"].max().date()


    #-------------------------
    # Normal CPI Graph
    #-------------------------

    min_value = min_date.strftime("%d %b %Y")
    max_value = max_date.strftime("%d %b %Y")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price Index line graph" )
    with col2:
        st.subheader("")

    graph_box(filtered_economic_data,INDEX_NAME,3,"price")

    #-------------------------
    # returns Graph
    #-------------------------

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("returns analysis" )
    with col2:
        st.subheader("")

    graph_box(filtered_returns_data,INDEX_NAME,3,"returns")

    #-------------------------
    # returns SQ Graph
    #-------------------------

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("square returns analysis" )
    with col2:
        st.subheader("")

    graph_box(filtered_sq_data,INDEX_NAME,3,"sq")

    #-------------------------
    # Volatility Graph
    #-------------------------

    min_value = min_date.strftime("%d %b %Y")
    max_value = max_date.strftime("%d %b %Y")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Volatility analysis" )
    with col2:
        st.subheader("7 and 30 day rolling volatility information")

    graph_box(filtered_v7_data,INDEX_NAME,3,"vol7")
    graph_box(filtered_v30_data,INDEX_NAME,3,"vol30")

else:
    st.write("No suitable index selected.")