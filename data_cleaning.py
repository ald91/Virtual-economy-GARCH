""" performs data cleaning activities in existing CSV files ready for interpretation"""

import pandas as pd

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, ANALYSIS_DATA_DIR, SUPPORTED_INDEX_LIST

def load_index(index_name:str) -> pd.DataFrame:
    """
    Loads a single OSRS Grand Exchange market index dataset from CSV.

    Reads stored market index data from the data directory and converts
    the CSV contents into a pandas DataFrame for further processing.

    Args:
        index_name (str): a supported CPI index string.

    Returns:
        pandas.DataFrame: DataFrame containing the market index observations.
    """

    file_path = RAW_DATA_DIR / f"{index_name}.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Market index file not found for {index_name} at: {file_path}")
    return pd.read_csv(file_path)

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

def save_index(index_name:str, data:pd.DataFrame) -> bool:
    """
    Saves a processed market index DataFrame as a CSV file.

    Args:
        data (pd.DataFrame): Processed market index data.
        index_name (str): Name of the market index.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        file_path = PROCESSED_DATA_DIR / f"{index_name}.csv"
        data.to_csv(file_path, index=False)

        return True

    except OSError as e:
        print(f"Failed to save {index_name}: {e}")
        return False

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
            indices[index_name] = load_index(index_name)

        except FileNotFoundError as e:
            print(e)

    return indices

def merge_indices(data:dict) -> bool:
    """ Merged all cleaned CSV files into one master file ready for analysis by column and matched by date.
        
        Args:
            data dict(CPI index : pd.dataframe).
        
        Returns:
            outcome bool.
    """
    merged_dataframe = None

    for index_name, dataframe in indices.items():

        # Rename price column to the index name
        dataframe = dataframe.rename(
            columns={"price": index_name}
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

def save_merged_frame(data:pd.DataFrame) -> bool:
    """
    saves the merged frame from merged_indices into the analysis directory as a csv.

    Args:
        data (pd.DataFrame)
    Returns:
        bool 
    """
    data.to_csv(f"{ANALYSIS_DATA_DIR}/master.csv", index=False)
    print("succesfully updated master and saved to CSV")
    return True

# running commands


indices = load_all_indices(SUPPORTED_INDEX_LIST)

for index_name, dataframe in indices.items():

    dataframe = clean_index(dataframe)
    dataframe = convert_timestamp(dataframe)

    indices[index_name] = dataframe

    save_index(index_name, dataframe)

indices = merge_indices(indices)
save_merged_frame(indices)