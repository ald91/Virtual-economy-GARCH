""" performs analytical functions on MASTER data only"""

import pandas as pd
from data_helper import load_csv, save_csv
from config import ANALYSIS_DATA_DIR

#=====================
# function definitions
#=====================

def calculate_percentage_change(master:pd.DataFrame) -> pd.DataFrame:
    """ calculates the daily percentage change for
    all data and indicies in the master frame and saves
    a new file for analysis"""
    data = master.copy()

    date = data["date"]
    data = data.drop(columns=["date"]).returns()
    data.insert(0,"date",date)
    return data

def calculate_percentage_change_squared(returns_dataframe:pd.DataFrame) -> pd.DataFrame:
    """ calculates the daily percentage change for
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
        "kurtosis": data.kurt()
    })

    statistics.index.name = "Market Index"

    return statistics

#=====================
# LOGIC
#=====================

#load master
master_df = load_csv("master", ANALYSIS_DATA_DIR)

#calculate pct change and save
pct_df = calculate_percentage_change(master_df)
save_csv("returns",pct_df,ANALYSIS_DATA_DIR)
stats = calculate_statistics(pct_df)
save_csv("returns_stats",stats,ANALYSIS_DATA_DIR,True)

#squares
pct_sq = calculate_percentage_change_squared(pct_df)
save_csv("squares", pct_sq, ANALYSIS_DATA_DIR)
pct_sq_stats = calculate_statistics(pct_sq)
save_csv("squares_stats",pct_sq_stats,ANALYSIS_DATA_DIR,True)

#calculate rolling vols
vol7=calculate_rolling_volatility(pct_df,7)
save_csv("rolling_vol_7",vol7,ANALYSIS_DATA_DIR)
vol7_stats = calculate_statistics(vol7)
save_csv("rolling_vol_7_stats",vol7_stats,ANALYSIS_DATA_DIR, True)

vol30=calculate_rolling_volatility(pct_df,30)
save_csv("rolling_vol_30",vol30,ANALYSIS_DATA_DIR)
vol30_stats = calculate_statistics(vol7)
save_csv("rolling_vol_30_stats",vol30_stats,ANALYSIS_DATA_DIR, True)
