""" performs analytical functions which build data required for GARCH analysis suitability"""

import pandas as pd

#=====================
# function definitions
#=====================

#BUG: indices are not saving uniform causing detection issues, consider .lower() or standardization earlier on.
def calculate_returns(master:pd.DataFrame) -> pd.DataFrame:
    """ calculates the daily returns for
    all data and indicies in the master frame and saves
    a new file for analysis"""
    data = master.copy()

    date = data["date"]
    data = data.drop(columns=["date"]).pct_change()
    data.insert(0,"date",date)
    return data

def calculate_returns_squared(returns_dataframe:pd.DataFrame) -> pd.DataFrame:
    """ calculates the daily returns for
    all data and indicies in the master frame and saves
    a new file for analysis"""
    data = returns_dataframe.copy()

    numeric_columns = data.select_dtypes(
        include="number"
    ).columns

    data[numeric_columns] = (
        data[numeric_columns] ** 2
    )

    return data

def calculate_rolling_volatility(returns_df:pd.DataFrame,time_window:int) -> pd.DataFrame:
    """ takes in a returns dataframe and applies a rolling volatility
    calculation based on the interval stated in days"""

    data = returns_df.copy()
    date = returns_df["date"]

    data = data.drop(columns="date")
    data = data.rolling(window=time_window).std()

    data.insert(0,"date",date)

    return data

def calculate_statistics(data: pd.DataFrame) -> pd.DataFrame:
    """ ONLY SUITABLE FOR frames which are not the master or events frames"""
    data = data.select_dtypes(include="number")

    statistics = pd.DataFrame({
        "mean": data.mean(),
        "std_dev": data.std(),
        "variance": data.var(),
        "min": data.min(),
        "max": data.max(),
        "skewness": data.skew(),
        "kurtosis": data.kurt() #NOTE: Excess kertosis NOT NORMAL (FISHERS DEFINITION)
    })

    statistics.index.name = "Market Index"

    return statistics
