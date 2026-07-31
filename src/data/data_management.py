""" combines data functions into simple function requests for users and updates meta data"""

from src.config import METADATA_JSON, EXOGENOUS_EVENTS_RAW, ECONOMY_RAW_CTI, SUPPORTED_INDEX_LIST
from src.data_helper import save_csv

import src.data.economy_loader as ecoloader
import src.data.economy_cleaner as ecocleaner
#import src.data.exogenous_events_loader
#import src.data.exogenous_events_cleaner

from datetime import datetime
import pandas as pd
import json


#===================
#Helper Functions
#===================
def load_metadata():
    """loads the metadata.json file in data/metadata"""
    with open(METADATA_JSON, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    return metadata

def save_metadata(metadata):
    """saves the metadata.json file in data/metadata"""
    with open(METADATA_JSON, "w",encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)
        print("metadata successfully updated")

def update_metadata(update_type="all",economic_path=ECONOMY_RAW_CTI,events_path=EXOGENOUS_EVENTS_RAW):
    """  updates the metadata.json object based on the update type"""

    metadata = load_metadata()
    update_time = datetime.now().strftime("%Y-%m-%d")
    valid_update_types = ["all","economic","events"]

    economic_data = pd.read_csv(economic_path, index_col="date")
    events_data = pd.read_csv(events_path, index_col="date")
  
    if update_type == valid_update_types[0]:
        metadata = {
        "economic_data": {
                "last_updated": update_time,
                "earliest_date": economic_data.index.min().strftime("%Y-%m-%d")
            },
            "event_data": {
                "last_updated": update_time,
                "earliest_date": events_data.index.min().strftime("%Y-%m-%d"),
                "total_events": len(events_data)
            }
        }
    elif update_type == valid_update_types[1]:
        metadata["economic_data"]["last_updated"] = update_time
        metadata["economic_data"]["earliest_date"] = economic_data.index.min().strftime("%Y-%m-%d")
    elif update_type == valid_update_types[2]:
        metadata["event_data"]["last_updated"] = update_time
        metadata["event_data"]["earliest_date"] = events_data.index.min().strftime("%Y-%m-%d")
        metadata["event_data"]["total_events"] = len(events_data)
    else:
        print("could not save metadata, the update type was not recognised.")
        return None
        
    save_metadata(metadata)

    return metadata

def updated_needed(update_type) -> bool:
    """ uses datetime to check if an update is needed"""
    METADATA = load_metadata()
    METADATA_LAST_UPDATED_CPI= METADATA["economic_data"]["last_updated"]
    METADATA_LAST_UPDATED_EVENTS=METADATA["event_data"]["last_updated"]

    today = datetime.now().date()
    if update_type == "economic":
        last_updated = METADATA_LAST_UPDATED_CPI
    elif update_type == "events":
        last_updated = METADATA_LAST_UPDATED_EVENTS
    else:
        return False
    print(last_updated)

    if last_updated is None:
        return True

    last_updated = datetime.strptime(last_updated, "%Y-%m-%d").date()

    if (today - last_updated).days >= 1:
        print("Update is required.")
        return True

    return False

#========================
#Functions
#========================

def update_economic_data():
    """ carries out a sequence of functions to update CPI data
    stored in the data DIR
    """
    update_type = "economic"
    data_status = updated_needed(update_type)
    if not data_status:
        return "an update is not required, the data is too recent"

    refresh_attempt = ecoloader.refresh_data()
    if not refresh_attempt:
        return "there was an error updating the economic data."
    return f"Economic data successfully updated to {datetime.today()}."

def clean_economic_data():
    """ carried out a sequence of functions to clean the CPI data stored
    in the data DIR"""
    indices = ecocleaner.load_all_indices(SUPPORTED_INDEX_LIST)

    for index_name, dataframe in indices.items():
        dataframe = ecocleaner.clean_index(dataframe)
        dataframe = ecocleaner.convert_timestamp(dataframe)
        indices[index_name] = dataframe
        save_csv(index_name, dataframe, RAW_DATA_DIR ,False)

    indices = ecocleaner.merge_indices(indices)
    save_csv("master",indices,ANALYSIS_DATA_DIR,False)
    return "economic data cleaning successful."

#TODO
def update_events_data():
    """ carries out a sequence of functions to update exogenous events data
    """
    update_type = "events"
    data_status = updated_needed(update_type)
    if not data_status:
        return "an update is not required, the data is too recent"

    refresh_attempt = el.refresh_data()
    if not refresh_attempt:
        return "there was an error updating the economic data."
    return f"Economic data successfully updated to {datetime.today()}."
