""" explores data using plotly library"""


import plotly.graph_objects as go
import pandas as pd
from statsmodels.tsa.stattools import acf, adfuller
from statsmodels.stats.diagnostic import het_arch
from arch import arch_model

from config import ANALYSIS_DATA_DIR, SUPPORTED_INDEX_LIST
from data_helper import load_csv

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
#HELPER FUNCTIONS
#=====================

#TODO: EVENTS FILTER an default state helper
def event_filer(event_category:str=all,
                event_scope:str=all,
                no_expected_impact:int=-1,
                new_item:int=-1,
                item_supply_change=-1,
                item_demand_change:int=-1,
                resource_availability_change:int=-1,
                new_resource_drop:int=-1,
                drop_rate_change:int=-1,
                temporary_demand:int=-1) -> list:
    """ takes in filter commands and returns a list of filters to apply to event dot plots in plotly figures"""
    event_filter_list = [event_category,event_scope,no_expected_impact,new_item,item_supply_change,item_demand_change,resource_availability_change,new_resource_drop,drop_rate_change,temporary_demand]
    return event_filter_list


#=====================
#INVESTIGATIVE FUNCTIONS
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

def plot_Acf_of_squared_returns(squared_returns_dataframe:pd.DataFrame, index_name:str) -> None:
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

def plot_arch_lm_test(returns_dataframe:pd.DataFrame, index_name:str) -> bool:
    """ prints ARCH-LM test to console. Test uses return data to investiage
    if observed volatility is explainable (it relies on previous volatility)
    if it does (Homoskedacity) the ARCH model is not appropriate and should
    NOT be used for the data (p > 0.05)"""

    p_value = int(0)
    lm_statistic = int(0)

    returns_data = returns_dataframe[f"{index_name}"].dropna()

    lm_statistic, p_value, f_statistic, f_p_value = het_arch(
    returns_data,
    nlags=30
)
    print("=================================================================================")
    print(f"\n lm value for {index_name} = {lm_statistic} \n p value for {index_name} = {p_value}")

    if p_value < 0.05 and p_value >= 0:
        print(f"The ARCH null hypothesis has been rejected for {index_name} as {p_value} is < 0.05. Modelling may be appropriate for this data. \n")
        print("=================================================================================")
        return True

    print(f"The ARCH null hypothesis has been rejected for {index_name} as {p_value} is > 0.05. Modelling is not supported for this data. \n")
    print("=================================================================================")
    return False
    
def adf_test (returns_dataframe:pd.DataFrame, index_name:str) -> bool:
    """ inspects a returns time series to deduce if a returns series
    is stationary or non-stationary. GARCH models require stationary
    returns series."""

    returns = returns_dataframe[f"{index_name}"].dropna()
    result = adfuller(returns)

    print(f"{index_name} ADF statistic:, ({result[0]}). \n{index_name} p-value: ({result[1]}). \n")

#=====================
#ARCH FUNCTIONS
#=====================
def garch_analysis(index_name:str,p:int,q:int,returns_dataframe:pd.DataFrame=RETURNS_ALL, sq_returns_dataframe:pd.DataFrame=RETURNS_SQ_ALL, events_dataframe:pd.DataFrame=EVENTS):
    """ performs the GARCH(X,Y) model where
        Args:
            index_name (str) is the name of the index to be analysed
            previous_variance_amount P (int) is the timeframe for volitility to be considered.
            previous_squared_armound Q (int) is the timeframe for squared returns to be considered.
    """

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
    event_y_position = results.conditional_volatility.max() * 1.1
    figure.add_trace(
        go.Scatter(
            x=EVENTS["date"],
            y=[5] * len(EVENTS),
            mode="markers",
            name="Events",
            text=EVENTS[["title","category","scope"]],
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
    #arch_possible = plot_arch_lm_test(returns_ALL,SELECTED_INDEX)
    #plot_Acf_of_squared_returns(returns_SQ_ALL, SELECTED_INDEX)
    #print(f"{SELECTED_INDEX} should be used for ARCH: {arch_possible}.
    #adf_test(RETURNS_ALL,SELECTED_INDEX)

garch_analysis("Common Trade Index",1,1)