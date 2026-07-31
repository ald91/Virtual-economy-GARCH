
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd

from src.config import SUPPORTED_INDEX_LIST

#=====================
#HELPER FUNCTIONS
#=====================



#=====================
#FUNCTIONS
#=====================
def plot_index_price(data: pd.DataFrame, index_name:str="all") -> None:
    """
    Plots OSRS market index price levels over time. specific indexes can be called, default is all

    Args:
        data (pd.DataFrame): Master index dataframe containing date column.
    """

    plot_data = data.copy()
    plot_data = plot_data.set_index("date")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:

        plot_data[index_name].plot(
            figsize=(12, 6),
                    title=f"OSRS Grand Exchange {index_name}"
        )
    else:
        plot_data.plot(
            figsize=(12, 6),
            title="OSRS Grand Exchange Market Indices"
        )

    plt.xlabel("Date")
    plt.ylabel("Index Price")
    plt.grid(True)
    plt.show()

def plot_returns(data: pd.DataFrame, index_name:str="all") -> None:
    """
    Plots daily percentage change for specific or all indices.

    Args:
        data (pd.DataFrame): Percentage change dataframe.
    """

    plot_data = data.copy()
    plot_data = plot_data.set_index("date")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:
        plot_data[index_name].plot(
            figsize=(12, 6),
                    title=f"OSRS {index_name} Daily Percentage Change"
        )
    else:
        plot_data.plot(
            figsize=(12, 6),
            title="OSRS Daily Percentage Change for all Trade Indices"
    )

    plt.xlabel("Date")
    plt.ylabel("Change")
    plt.grid(True)
    plt.show()

def plot_volatility(data: pd.DataFrame, index_name:str="all") -> None:
    """
    Plots rolling volatility for specific indices or all.

    Args:
        data (pd.DataFrame): Rolling volatility dataframe.
    """

    plot_data = data.copy()
    plot_data = plot_data.set_index("date")

    if index_name != "all" and index_name in SUPPORTED_INDEX_LIST:
        plot_data[index_name].plot(
            figsize=(12, 6),
                    title=f"OSRS {index_name} 30 Day Rolling Volatility."
        )
    else:
        plot_data.plot(
            figsize=(12, 6),
            title="30 Day Rolling Volatility"
        )

    plt.xlabel("Date")
    plt.ylabel("Volatility")
    plt.grid(True)
    plt.show()

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
