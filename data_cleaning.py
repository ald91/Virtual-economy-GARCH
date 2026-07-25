""" performs data cleaning activities in existing CSV files ready for interpretation"""

import pandas as pd

from config import ANALYSIS_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, SUPPORTED_INDEX_LIST
from data_helper import load_csv, save_csv


#=====================
# function definitions
#=====================

def clean_index(data:pd.DataFrame) -> pd.DataFrame:
    """ Takes a loaded dataframe and removes unwanted columns from the CSV.

    Args:
        data (pd.DataFrame): Processed market index data.

    Returns:
        pd.DataFrame
    """
    data = dataframe.drop(
        columns=["id","volume"],
        errors="ignore"
    )

    return data

def convert_timestamp(data:pd.DataFrame) -> pd.DataFrame:
    """
    Converts Unix timestamps into Python datetime objects and
    sets the column order to [ date , price ].

    Transforms ms timestamps provided by the Grand Exchange
    Market Watch API into datetime values.

    Args:
    data (pd.DataFrame): Processed market index data.

    Returns:
        pandas.DataFrame: DataFrame containing converted datetime values.
    """

    data["date"] = (
        pd.to_datetime(
            data["timestamp"],
            unit="ms"
        )
        .dt.normalize()
    )

    data = data.drop(
        columns=["timestamp"],
        errors="ignore"
    )

    # SAMPLE FREQUENCY =  one observation per day
    data = (
        data
        .groupby("date", as_index=False)
        .last()
    )

    data = data[["date", "price"]]

    return data

def load_all_indices(index_names: list[str]) -> dict[str, pd.DataFrame]:
    """
    Loads all supported OSRS Grand Exchange market indices from config.py.

    Args:
        index_names (list[str]).

    Returns:
        dict[str, pd.DataFrame].
    """

    indices = {}

    for index_name in index_names:
        try:
            indices[index_name] = load_csv(index_name,RAW_DATA_DIR)

        except FileNotFoundError as e:
            print(e)

    return indices

def merge_indices(data:dict[str,pd.DataFrame]) -> pd.DataFrame:
    """ Merged all cleaned CSV files into one master file ready 
    for analysis by column and matched by date.
        
        Args:
            data dict(CPI index : pd.dataframe).
        
        Returns:
            outcome bool.
    """
    merged_dataframe = None

    for index, index_dataframe in data.items():

        # Rename price column to the index name
        dataframe = index_dataframe.rename(
            columns={"price": index}
        )

        if merged_dataframe is None:
            merged_dataframe = dataframe

        else:
            merged_dataframe = merged_dataframe.merge(
                dataframe,
                on="date",
                how="inner",
                validate="one_to_one"
            )

    return merged_dataframe

#===================
# running commands
#===================
indices = load_all_indices(SUPPORTED_INDEX_LIST)

for index_name, dataframe in indices.items():

    dataframe = clean_index(dataframe)
    dataframe = convert_timestamp(dataframe)

    indices[index_name] = dataframe

    save_csv(index_name, dataframe, RAW_DATA_DIR ,False)

indices = merge_indices(indices)
save_csv("master",indices,ANALYSIS_DATA_DIR,False)
