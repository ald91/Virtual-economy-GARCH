
import streamlit as st
from src.visualisation.plot_graph import *

import pandas as pd

from src.config import ANALYSIS_DATA_DIR

def graph_box(graph_data,index_name,rounding,graph_type):

    #element preparation
    #-------------------------
    index_name = str(index_name)

    metrics =  None


    if graph_type == "price":
        graph = plot_time_series(graph_data,index_name,title=f"OSRS Grand Exchange {index_name.title()}")
    elif graph_type == "returns" or graph_type == "sq":
        graph = plot_time_series(graph_data,index_name,title=f"OSRS {index_name.title()} Daily Returns)")
        metrics = pd.read_csv(ANALYSIS_DATA_DIR/"returns_stats.csv")
    elif graph_type == "vol30":
        graph = plot_time_series(graph_data,index_name,title=f"OSRS {index_name.title()} 30 Day Rolling Volatility")
        metrics = pd.read_csv(ANALYSIS_DATA_DIR/"vol_30_stats.csv")
    elif graph_type == "vol7":
        graph = plot_time_series(graph_data,index_name,title=f"OSRS {index_name.title()} 7 Day Rolling Volatility")
        metrics = pd.read_csv(ANALYSIS_DATA_DIR/"vol_7_stats.csv")
    else:
        graph = "unsupport graph request"

    if metrics is None:
        std_dev = "not reported"
        skewness = "not reported"
        kurtosis = "not reported"

    else:
        std_dev = round(metrics.loc[metrics["Market Index"] == index_name,"std_dev"].iloc[0],8)
        skewness = round(metrics.loc[metrics["Market Index"] == index_name,"skewness"].iloc[0],rounding)
        kurtosis = round(metrics.loc[metrics["Market Index"] == index_name,"kurtosis"].iloc[0],rounding)
   

    #-------------------------
    
    st.divider()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Lowest Value", f"{round(graph_data[index_name].min(),rounding)}")
    col2.metric("Highest Value", f"{round(graph_data[index_name].max(),rounding)}")
    col3.metric("Range", f"{round(graph_data[index_name].max() - graph_data[index_name].min(),4)}")
    col4.metric("standard deviation", std_dev)
    col5.metric("skewness", skewness)
    col6.metric("kertosis", kurtosis)


    st.divider()

    fig = graph

    if fig is None:
        st.divider()
        return

    st.plotly_chart(fig,width='stretch')
    st.divider()