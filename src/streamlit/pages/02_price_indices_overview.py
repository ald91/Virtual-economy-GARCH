
import streamlit as st
import pandas as pd

from streamlit_plotly_events import plotly_events

from src.config import ECONOMY_MASTER_DATA, SUPPORTED_INDEX_LIST
from src.visualisation.plot_graph import plot_index_price

#------------------------
# Page Config
#------------------------

st.set_page_config(
    page_title="Economy Index Price Overview",
    page_icon="📈",
    layout="wide"
)

#------------------------
# Load Data
#------------------------
ECONOMIC_DATA = pd.read_csv(ECONOMY_MASTER_DATA)
ECONOMIC_DATA["date"] = pd.to_datetime(ECONOMIC_DATA["date"],errors="coerce")






#------------------------
# Title
#------------------------

st.title("📈 Economic Data Overview Page")
st.write(
    """
        On this page you can see relavent information about each
        price index followed by the application according to available
        Runescape Grand Exchange Market Watch API data. And a small amount
        of application calculated statistics.
    """
)

#------------------------
#date filter
#------------------------

min_date = ECONOMIC_DATA["date"].min().date()
max_date = ECONOMIC_DATA["date"].max().date()

selected_dates = st.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_economic_data = ECONOMIC_DATA

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_economic_data = ECONOMIC_DATA[
        (ECONOMIC_DATA["date"].dt.date >= start_date) &
        (ECONOMIC_DATA["date"].dt.date <= end_date)
    ]

min_date = filtered_economic_data["date"].min().date()
max_date = filtered_economic_data["date"].max().date()

# -----------------------
# Graphs
# -----------------------
st.divider()
for index in SUPPORTED_INDEX_LIST:
    min_value = min_date.strftime("%d %b %Y")
    max_value = max_date.strftime("%d %b %Y")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(index.title())
    with col2:
        st.page_link("pages/03_price_index_details.py",label="Click Here For Detailed statistics",query_params={"index": index})

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Lowest Value Date & Value", f"{min_value} ({filtered_economic_data[index].min()})" )
    col2.metric("Highest Value Date & Value", f"{max_value} ({filtered_economic_data[index].max()})")
    col3.metric("Range", filtered_economic_data[index].max() - filtered_economic_data[index].min())

    fig = plot_index_price(filtered_economic_data,index)
    st.plotly_chart(fig,width='stretch')
    st.divider()


