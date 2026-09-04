""" explores data using plotly library"""


import plotly.graph_objects as go
import pandas as pd

from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import het_arch
from arch import arch_model

from src.config import ANALYSIS_DATA_DIR, SUPPORTED_INDEX_LIST
from src.data_helper import load_csv

#====================
#DATA SETS
#====================
EVENTS = load_csv("events index", ANALYSIS_DATA_DIR)
CPI_ALL = load_csv("master", ANALYSIS_DATA_DIR)


RETURNS_ALL = load_csv("returns",ANALYSIS_DATA_DIR).set_index("date")
RETURNS_STATS = load_csv("returns_stats", ANALYSIS_DATA_DIR).set_index("Market Index")

RETURNS_SQ_ALL = load_csv("squares", ANALYSIS_DATA_DIR).set_index("date")
RETURNS_SQ_ALL_STATS = load_csv("squares_stats", ANALYSIS_DATA_DIR).set_index("Market Index")

ROLLING_VOL_30 = load_csv("rolling_vol_30",ANALYSIS_DATA_DIR).set_index("date")
ROLLING_VOL_30_STATS = load_csv("rolling_vol_30_stats", ANALYSIS_DATA_DIR).set_index("Market Index")

ROLLING_VOL_7 = load_csv("rolling_vol_7",ANALYSIS_DATA_DIR).set_index("date")
ROLLING_VOL_7_STATS = load_csv("rolling_vol_7_stats", ANALYSIS_DATA_DIR).set_index("Market Index")


#=====================
#GARCH FUNCTIONS
#=====================

def arch_lm_test(returns:pd.DataFrame) -> pd.DataFrame:
    """ Creates a dataframe and CSV of the results. Test uses return data to investiage
    if observed volatility is explainable (it relies on previous volatility)
    if it does (Homoskedacity) the ARCH model is not appropriate and should
    NOT be used for the data (p > 0.05)"""

    results = []

    for index in SUPPORTED_INDEX_LIST:
        column_name = index.title()
        returns_data = returns[column_name].dropna()

        lm_statistic, p_value, f_statistic, f_p_value = het_arch(
            returns_data,
            nlags=30
        )

        results.append({
            "index": column_name,
            "lm_statistic": lm_statistic,
            "p_value": p_value,
            "f_statistic": f_statistic,
            "f_p_value": f_p_value,
            "arch_suitable": p_value < 0.05
        })

    return pd.DataFrame(results)
    
def adf_test (returns:pd.DataFrame) -> pd.DataFrame:
    """ inspects a returns time series to deduce if a returns series
    is stationary or non-stationary. GARCH models require stationary
    returns series."""

    results = []

    for index in SUPPORTED_INDEX_LIST:
        column_name = index.title()
        returns_data = returns[column_name].dropna()
        adf_statistic, p_value, used_lags, nobs, critical_values, icbest = adfuller(returns_data)

        results.append({
            "index": column_name,
            "adf statistic": adf_statistic,
            "adf_p_value": p_value,
            "stationary": p_value < 0.05
        })

        return pd.DataFrame(results)

def garch_analysis(index_name:str,p:int,q:int,returns_dataframe:pd.DataFrame=RETURNS_ALL, events_dataframe:pd.DataFrame=EVENTS, category_filter:str="all",scope_filter: str = "all"):
    """ performs the GARCH(X,Y) model where
        Args:
            index_name (str) is the name of the index to be analysed
            previous_variance_amount P (int) is the timeframe for volitility to be considered.
            previous_squared_armound Q (int) is the timeframe for squared returns to be considered.
    """

    filtered_events = events_dataframe

    if category_filter != "all":
        filtered_events = filtered_events[
            filtered_events["category"] == category_filter
        ]

    if scope_filter != "all":
        filtered_events = filtered_events[
            filtered_events["scope"] == scope_filter
        ]

    #convert values to % for GARCH
    returns = returns_dataframe[f"{index_name}"].dropna() * 100

    model = arch_model(
    returns,
    mean="Constant",
    vol="GARCH",
    p=p,
    q=q,
    dist="t"
    )

    results = model.fit(disp="off")
    print(results.summary())

    #plot graph of conditional volatility
    figure = go.Figure()

    # Add event trace
    figure.add_trace(
        go.Scatter(
            x=filtered_events["date"],
            y=[5] * len(filtered_events),
            mode="markers",
            name="Events",
            text=filtered_events[["title","category","scope"]],
            hovertemplate=(
                "Date: %{x}<br>"
                "Event: %{text[0]}<br>"
                "Category: %{text[1]}<br>"
                "Scope: %{text[2]}<br>"
                "<extra></extra>"
            )
        )
    )
    
    figure.add_trace(
        go.Scatter(
            x=returns.index,
            y=results.conditional_volatility,
            mode="lines",
            name="GARCH Conditional Volatility"
        )
    )

    figure.update_layout(
        title=f"{index_name} GARCH({p},{q}) Conditional Volatility",
        xaxis_title="Date",
        yaxis_title="Estimated Volatility"
    )

    figure.update_yaxes(
    range=[0, 6]
    )

    print(returns.head())
    print(results.conditional_volatility.head())
    figure.show()





#=====================
#EXCUTE
#=====================

#plot_event_investigation(returns_ALL,returns_STATS,EVENTS,SELECTED_INDEX,"Returns")
#plot_event_investigation(returns_SQ_ALL,returns_SQ_ALL_STATS,EVENTS,SELECTED_INDEX,"Returns")
#plot_event_investigation(ROLLING_VOL_7, ROLLING_VOL_7_STATS,EVENTS,SELECTED_INDEX, "Rolling Volatility over 7 days")
#plot_event_investigation(ROLLING_VOL_30, ROLLING_VOL_30_STATS,EVENTS,SELECTED_INDEX, "Rolling Volatility over 30 days")
#plot_Acf_of_squared_returns(returns_SQ_ALL, SELECTED_INDEX)

#for SELECTED_INDEX in SUPPORTED_INDEX_LIST:
    #arch_possible = arch_lm_test(RETURNS_ALL,SELECTED_INDEX.title())
    #plot_Acf_of_squared_returns(returns_SQ_ALL, SELECTED_INDEX)
    #print(f"{SELECTED_INDEX} should be used for ARCH: {arch_possible}.
    #adf_test(RETURNS_ALL,SELECTED_INDEX.title())

#GARCH_INDEX = ["common trade index","food index", "herb index"]
#for SELECTED_INDEX in GARCH_INDEX:
#    garch_analysis(SELECTED_INDEX,1,1,category_filter="New Content",scope_filter="Whole Economy")
