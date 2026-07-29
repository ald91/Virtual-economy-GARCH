"""Functions for visualising OSRS market data."""

import matplotlib.pyplot as plt
import pandas as pd
from config import SUPPORTED_INDEX_LIST

#=====================
# function definitions
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
