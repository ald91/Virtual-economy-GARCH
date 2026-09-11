
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.config import SUPPORTED_INDEX_LIST

SUPPORTED_INDEX_LIST = list(SUPPORTED_INDEX_LIST)

#=====================
#FUNCTIONS
#=====================

def plot_time_series(data: pd.DataFrame,index_name: str = "all",title: str = "OSRS Market Indices",y_axis_title: str = "Value") -> go.Figure:


    plot_data = data.copy()
    plot_data["date"] = pd.to_datetime(plot_data["date"],errors="coerce")
    
    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:
        fig = px.line(
            plot_data,
            x="date",
            y=index_name,
            title=title
        )
    else:
        fig = px.line(
            plot_data,
            x="date",
            y=SUPPORTED_INDEX_LIST,
            title=title
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=y_axis_title,
        height=600
    )

    return fig

def plot_events_graph(event_data:pd.DataFrame) -> go.Figure:
    """ processes the events index.csv to return a interactable
    figure using plotly"""

    data = event_data.copy()
    data["date"] = pd.to_datetime(data["date"])

    fig = px.scatter(
        data,
        x="date",
        y="category",
        hover_data=[
            "title",
        ],
        title="Exogenous Event Timeline",
    )

    fig.update_traces(
        marker=dict(size=10),
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Event Category",
        
        height=600,
    )

    return fig

def plot_index_price(data: pd.DataFrame, index_name:str="all") -> go.Figure:
    """
    Plots OSRS market index price levels over time. specific indexes can be called, default is all

    Args:
        data (pd.DataFrame): Master index dataframe containing date column.
    """

    plot_data = data.copy()
    plot_data["date"] = pd.to_datetime(plot_data["date"],errors="coerce")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:

        fig = px.line(
            plot_data,
            x="date",
            y=index_name,
            title=f"OSRS Grand Exchange {index_name.title()}",
        )

    else:

        fig = px.line(
            plot_data,
            x="date",
            y=SUPPORTED_INDEX_LIST,
            title="OSRS Grand Exchange Market Indices",
        )


    return fig

def plot_returns(data: pd.DataFrame,index_name: str = "all") -> go.Figure:
    """
    Creates a Plotly line graph showing daily returns
    for a specific market index or all market indices.

    Args:
        data: Returns dataframe.
        index_name: Market index to plot, or "all".

    Returns:
        Plotly Figure.
    """

    plot_data = data.copy()
    plot_data["date"] = pd.to_datetime(plot_data["date"],errors="coerce")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:

        fig = px.line(
            plot_data,
            x="date",
            y=index_name,
            title=f"OSRS {index_name.title()} Daily Returns"
        )

    else:

        fig = px.line(
            plot_data,
            x="date",
            y=SUPPORTED_INDEX_LIST,
            title="OSRS Daily Returns for All Trade Indices"
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Return",
        height=600
    )

    return fig

def plot_volatility(data: pd.DataFrame,index_name: str = "all") -> go.Figure:
    """
    Creates a Plotly line graph showing rolling volatility
    for a specific index or all market indices.

    Args:
        data (pd.DataFrame): Rolling volatility dataframe.
        index_name (str): Market index to plot, or "all".

    Returns:
        go.Figure: Plotly figure containing the volatility graph.
    """

    plot_data = data.copy()
    plot_data["date"] = pd.to_datetime(plot_data["date"],errors="coerce")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:

        fig = px.line(
            plot_data,
            x="date",
            y=index_name,
            title=f"OSRS {index_name.title()} 30 Day Rolling Volatility"
        )

    else:

        fig = px.line(
            plot_data,
            x="date",
            y=SUPPORTED_INDEX_LIST,
            title="OSRS 30 Day Rolling Volatility"
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Volatility",
        height=600
    )

    return fig

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

def plot_event_investigation(timeseries_dataframe:pd.DataFrame, statistics:pd.DataFrame, events_data: pd.DataFrame, index_name: str,plot_metric:str) -> None:
    """
    Plots volatility with selected event category marked.
    """
    # Filter events by chosen category
    filtered_events = events_data

    start_date = "2020-06-15"

    timeseries_dataframe = timeseries_dataframe[
    timeseries_dataframe["date"] >= start_date
]


    #identify statistical flags
    index_mean = statistics.loc[index_name, "mean"]
    index_std_dev = statistics.loc[index_name,"std_dev"]

    #set up flags
    #Unusual positive moves:
    positive_flag2 = index_mean + 2 * index_std_dev
    print(positive_flag2)
    positive_flag = index_mean + index_std_dev
    print(positive_flag)

    #Unusual negative move:
    negative_flag2 = index_mean - 2 * index_std_dev
    print(negative_flag2)
    negative_flag = index_mean - index_std_dev
    print(negative_flag)

    figure = go.Figure()

    # Exogenous events trace
    figure.add_trace(
        go.Scatter(
            x=filtered_events["date"],
            y=[timeseries_dataframe[index_name].max() * 0.1] * len(events_data),
            mode="markers",
            name="exogenous events",
            text=events_data["title"],
            hovertemplate=(
                "Date: %{x}<br>"
                "Event: %{text}<br>"
            )
        )
    )

    # Plot +ve flag lines
    figure.add_trace(
        go.Scatter(
            x=timeseries_dataframe["date"],
            y=[positive_flag2] * len(timeseries_dataframe),
            mode="lines",
            name="mean + 2std dev"
        )
    )

    figure.add_trace(
        go.Scatter(
            x=timeseries_dataframe["date"],
            y=[positive_flag] * len(timeseries_dataframe),
            mode="lines",
            name="mean + std dev"
        )
    )

    # Plot -ve flag lines
    figure.add_trace(
        go.Scatter(
            x=timeseries_dataframe["date"],
            y=[negative_flag2] * len(timeseries_dataframe),
            mode="lines",
            name="mean - 2std dev"
        )
    )

    figure.add_trace(
        go.Scatter(
            x=timeseries_dataframe["date"],
            y=[negative_flag] * len(timeseries_dataframe),
            mode="lines",
            name="mean - std dev"
        )
    )


    # Plot time series line
    figure.add_trace(
        go.Scatter(
            x=timeseries_dataframe["date"],
            y=timeseries_dataframe[index_name],
            mode="lines",
            name=index_name
        )
    )


    figure.update_layout(
        title=f"{index_name} plotted against {plot_metric}",
        xaxis_title="Date",
        yaxis_title=f"{plot_metric}"
    )

    figure.show()

def plot_acf_of_squared_returns(squared_returns_dataframe:pd.DataFrame, index_name:str) -> None:
    """ takes squared returns data of a CPI and plots Auto-correlation function. this assists in understanding if
    a time series dataset. result 1 is removed as lag 1 is always == 1.
    """

    squared_returns_dataframe = squared_returns_dataframe[f"{index_name}"]

    figure = go.Figure()

    acf_values = acf(squared_returns_dataframe.dropna(),nlags=30)
    acf_values = acf_values[1:]

    print(f" acf values for {index_name}. \n {acf_values}")
    print("=================================================================================")
    
    lags = list(range(len(acf_values)))

    figure.add_trace(
        go.Bar(
            x=lags,
            y=acf_values,
            name="ACF Squared Returns"
        )
    )

    figure.update_layout(
        title=f"ACF of Squared Returns for {index_name}",
        xaxis_title="Lag",
        yaxis_title="Auto Correlation"
    )

    figure.show()
