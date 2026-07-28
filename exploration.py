""" explores data using plotly library"""

import plotly.graph_objects as go
import pandas as pd

from config import ANALYSIS_DATA_DIR
from data_helper import load_csv

#====================
#DATA SETS
#====================
EVENTS = load_csv("events index", ANALYSIS_DATA_DIR)
CPI_ALL = load_csv("master", ANALYSIS_DATA_DIR)
PCT_CHANGE_ALL = load_csv("pct_change",ANALYSIS_DATA_DIR)
PCT_CHANGE_SQ_ALL = load_csv("squares", ANALYSIS_DATA_DIR)
ROLLING_VOLATILITY_30 = load_csv("rolling_vol_30",ANALYSIS_DATA_DIR)
ROLLING_VOLATILITY_7 = load_csv("rolling_vol_7",ANALYSIS_DATA_DIR)
PCT_CHANGE_STATS = load_csv("pct_change_stats", ANALYSIS_DATA_DIR)
PCT_CHANGE_STATS = PCT_CHANGE_STATS.set_index("Market Index")

#=====================
#PLOTTING FUNCTIONS
#=====================

def plot_volatility_events(volatility_30_data: pd.DataFrame, volatility_7_data:pd.DataFrame, events_data: pd.DataFrame, index_name: str) -> None:
    """
    Plots volatility with selected event category marked.
    """

    # Filter events by chosen category
    filtered_events = events_data[
        events_data["category"] == event_category
    ]

    figure = go.Figure()

    # Plot volatility line
    figure.add_trace(
        go.Scatter(
            x=volatility_30_data["date"],
            y=volatility_30_data[index_name],
            mode="lines",
            name=index_name
        )
    )
    
    # Plot volatility line
    figure.add_trace(
        go.Scatter(
            x=volatility_7_data["date"],
            y=volatility_7_data[index_name],
            mode="lines",
            name=index_name
        )
    )
    
    # Add event dots
    figure.add_trace(
        go.Scatter(
            x=filtered_events["date"],
            y=[volatility_30_data[index_name].max() * 0.1] * len(filtered_events),
            mode="markers",
            name=event_category,
            text=filtered_events["title"],
            hovertemplate=(
                "Date: %{x}<br>"
                "Event: %{text}<br>"
                "Category: " + event_category +
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title=f"{index_name} with {event_category} Events",
        xaxis_title="Date",
        yaxis_title="Volatility"
    )

    figure.show()

def plot_percentage_change_events(percentage_change:pd.DataFrame, percantage_change_stats:pd.DataFrame, events_data: pd.DataFrame, index_name: str) -> None:
    """
    Plots volatility with selected event category marked.
    """
    # Filter events by chosen category
    filtered_events = events_data

    #identify statistical flags
    index_mean = percantage_change_stats.loc[index_name, "mean"]
    index_std_dev = percantage_change_stats.loc[index_name,"std_dev"]

    #set up flags
    #Unusual positive move:   mean + (2 × std_dev)
    positive_flag = index_mean + 2 * index_std_dev
    print(positive_flag)

    #Unusual negative move: mean - (2 × std_dev)
    negative_flag = index_mean - 2 * index_std_dev
    print(negative_flag)

    figure = go.Figure()

        # Plot +ve flag line
    figure.add_trace(
        go.Scatter(
            x=percentage_change["date"],
            y=[positive_flag] * len(percentage_change),
            mode="lines",
            name="mean + 2std dev"
        )
    )

            # Plot -ve flag line
    figure.add_trace(
        go.Scatter(
            x=percentage_change["date"],
            y=[negative_flag] * len(percentage_change),
            mode="lines",
            name="mean - 2std dev"
        )
    )


    # Plot volatility line
    figure.add_trace(
        go.Scatter(
            x=percentage_change["date"],
            y=percentage_change[index_name],
            mode="lines",
            name=index_name
        )
    )

    # Add event dots
    figure.add_trace(
        go.Scatter(
            x=filtered_events["date"],
            y=[percentage_change[index_name].max() * 0.1] * len(events_data),
            mode="markers",
            name="exogenous events",
            text=events_data["title"],
            hovertemplate=(
                "Date: %{x}<br>"
                "Event: %{text}<br>"
            )
        )
    )

    figure.update_layout(
        title=f"{index_name} with All exogenous events",
        xaxis_title="Date",
        yaxis_title="Percentag Change"
    )

    figure.show()

#=====================
#EXCUTE
#=====================
#plot_volatility_events(ROLLING_VOLATILITY_30,ROLLING_VOLATILITY_7,EVENTS,"Rune Index","New Content")
plot_percentage_change_events(PCT_CHANGE_ALL,PCT_CHANGE_STATS,EVENTS,"Food Index")
