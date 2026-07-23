"""Functions for visualising OSRS market data."""

import matplotlib.pyplot as plt
import pandas as pd

def plot_index_prices(data: pd.DataFrame) -> None:
    """
    Plots OSRS market index price levels over time.

    Args:
        data (pd.DataFrame): Master index dataframe containing date column.
    """

    plot_data = data.copy()
    plot_data = plot_data.set_index("date")

    plot_data.plot(
        figsize=(12, 6),
        title="OSRS Grand Exchange Market Indices"
    )

    plt.xlabel("Date")
    plt.ylabel("Index Price")
    plt.grid(True)

    plt.show()

def plot_pct_change(data: pd.DataFrame) -> None:
    """
    Plots daily percentage change.

    Args:
        data (pd.DataFrame): Percentage change dataframe.
    """

    plot_data = data.copy()

    plot_data = plot_data.set_index("date")

    plot_data.plot(
        figsize=(12, 6),
        title="Daily Percentage Change"
    )

    plt.xlabel("Date")
    plt.ylabel("Change")

    plt.grid(True)

    plt.show()

def plot_volatility(data: pd.DataFrame) -> None:
    """
    Plots rolling volatility.

    Args:
        data (pd.DataFrame): Rolling volatility dataframe.
    """

    plot_data = data.copy()
    plot_data = plot_data.set_index("date")

    plot_data.plot(
        figsize=(12, 6),
        title="30 Day Rolling Volatility"
    )

    plt.xlabel("Date")
    plt.ylabel("Volatility")

    plt.grid(True)

    plt.show()