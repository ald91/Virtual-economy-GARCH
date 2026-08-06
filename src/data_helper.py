""" contains functions which are useful to all data_x.py files"""

import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, ANALYSIS_DATA_DIR

#=====================
# function definitions
#=====================

def load_csv(sheet_name:str, target_dir:Path,set_index=None) -> pd.DataFrame | None:
    """ loads the target sheet to the application"""
    file_path = target_dir/f"{sheet_name}.csv"
    if not file_path.exists():
        return None
    df = pd.read_csv(file_path)
    if set_index is not None:
        df = df.set_index(f"{set_index}")
    return df

def save_csv(sheet_name:str, data:pd.DataFrame, target_dir:Path, save_index:bool=False) -> bool:
    """
    Saves a DataFrame as a CSV file.

    Args:
        sheet_name (str): the name of the target file.
        data (pd.DataFrame): dataframe variable.
        save index (bool): should the index be preserved (default=FALSE).
        taret_dir (str): the target directory where the file is located.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        file_path = f"{target_dir}/{sheet_name}.csv"
        data.to_csv(file_path, index=save_index)

        return True

    except OSError as e:
        print(f"Failed to save {sheet_name} at location {target_dir}: {e}")
        return False
