""" performs analytical functions on MASTER data only"""

import pandas as pd

from config import ANALYSIS_DATA_DIR
from visualisation import plot_index_prices, plot_pct_change, plot_volatility
from data_helper import save_csv, load_csv

def calculate_percentage_change(master:pd.DataFrame) -> pd.DataFrame:
    """ calculates the daily percentage change for
    all data and indicies in the master frame and saves
    a new file for analysis"""
    data = master.copy()

    date = data["date"]
    data = data.drop(columns=["date"]).pct_change()
    data.insert(0,"date",date)
    return data

def calculate_rolling_volatility(data:pd.DataFrame,time_window:int) -> pd.DataFrame:
    """ takes in a pct_change dataframe and applies a rolling volatility
    calculation based on the interval stated in days"""

    data = pct_change_df.copy()
    date = pct_change_df["date"]

    data = data.drop(columns="date")
    data = data.rolling(window=time_window).std()

    data.insert(0,"date",date)

    return data

def calculate_statistics(data: pd.DataFrame) -> pd.DataFrame:
    """ ONLY SUITABLE FOR THE % CHANGE DF"""
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

#===================
# running commands
#===================

master_frame = load_csv("master",ANALYSIS_DATA_DIR)

#calculation of % change
pct_change_df = calculate_percentage_change(master_frame)
save_csv("pct_change",pct_change_df,ANALYSIS_DATA_DIR)

#data suitability step for modelling economy
pct_change_stats_df = calculate_statistics(pct_change_df)
save_csv("pct_change_stats",pct_change_stats_df,ANALYSIS_DATA_DIR,save_index=True)

#calculation of volatility
rolling_volatility_df = calculate_rolling_volatility(pct_change_df,30)
save_csv("rolling_vol_30",rolling_volatility_df,ANALYSIS_DATA_DIR)

plot_index_prices(master_frame)
plot_pct_change(pct_change_df)
plot_volatility(rolling_volatility_df)
