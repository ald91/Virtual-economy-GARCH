import streamlit as st
import pandas as pd

from streamlit_plotly_events import plotly_events

from src.config import EVENTS_MASTER_DATA
from src.visualisation.plot_graph import plot_events_graph

# -----------------------
# Page Config
# -----------------------

st.set_page_config(
    page_title="Exogenous Events List",
    page_icon="📈",
    layout="wide"
)


# -----------------------
# Load Data
# -----------------------

EVENTS_INDEX = pd.read_csv(EVENTS_MASTER_DATA)
EVENTS_INDEX["date"] = pd.to_datetime(EVENTS_INDEX["date"],errors="coerce")


# -----------------------
# Title
# -----------------------

st.title("📈 Complete exogenous events history and data table")

st.write(
    """
    This table displays all recognised and categorised exogenous events
    stored and filtered in the application files.
    """
)

st.divider()


# -----------------------
# Event Filters
# -----------------------


categories = sorted(EVENTS_INDEX["category"].dropna().unique())

col1, col2 = st.columns(2)

with col1:
    st.write("Event Categories")

    selected_categories = []

    for start in range(0, len(categories), 5):

        row_categories = categories[start:start + 5]
        category_cols = st.columns(5)

        for i, category in enumerate(row_categories):
            with category_cols[i]:
                if st.checkbox(category, value=True):
                    selected_categories.append(category)
                    

with col2:
    min_date = EVENTS_INDEX["date"].min().date()
    max_date = EVENTS_INDEX["date"].max().date()

    selected_dates = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

filtered_events = EVENTS_INDEX[
    EVENTS_INDEX["category"].isin(selected_categories)
]

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_events = filtered_events[
        (filtered_events["date"].dt.date >= start_date) &
        (filtered_events["date"].dt.date <= end_date)
    ]

# -----------------------
# Event Statistics
# -----------------------

TOTAL_EVENTS = len(filtered_events)

col1, col2, col3 = st.columns(3)

if filtered_events.empty:

    col1.metric("Total Events", 0)
    col2.metric("Earliest Event", "No Events")
    col3.metric("Latest Event", "No Events")

else:

    OLDEST_EVENT = filtered_events["date"].min()
    NEWEST_EVENT = filtered_events["date"].max()

    col1.metric("Total Events", TOTAL_EVENTS)
    col2.metric("Earliest Event",OLDEST_EVENT.strftime("%d %b %Y"))
    col3.metric("Latest Event",NEWEST_EVENT.strftime("%d %b %Y"))
    
# -----------------------
# Event Timeline
# -----------------------
event_graph = plot_events_graph(filtered_events)
selected_points = plotly_events(
    event_graph,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=600
)

if selected_points:

    point_index = selected_points[0]["pointIndex"]
    selected_event = filtered_events.iloc[[point_index]]


# -----------------------
# Event Table
# -----------------------

st.subheader("Selected Event")

if selected_points:

    point_index = selected_points[0]["pointIndex"]
    selected_event = filtered_events.iloc[[point_index]]

    st.dataframe(
        selected_event,
        width='stretch',
        hide_index=True
    )

else:
        st.dataframe(
        filtered_events,
        width='stretch',
        hide_index=True
    )