""" contains numerous functions such as filters that simplify page code syntax"""

from pandas import DataFrame
from datetime import datetime

def filter_dataframe(dataframe:DataFrame,col:str,start_date:datetime,end_date:datetime) -> DataFrame:
    """ performs a simple function to allow filtering on a streamlit page to apply to all elements"""

    filtered_data = dataframe[
        (dataframe[col].dt.date >= start_date) &
        (dataframe[col].dt.date <= end_date)
    ]

    return filtered_data
