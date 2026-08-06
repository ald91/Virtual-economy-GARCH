""" combines data functions into simple function requests for users and updates meta data"""
from datetime import datetime
from pathlib import Path
import json
import pandas as pd

from src.config import METADATA_JSON, ECONOMY_MASTER_DATA, EVENTS_MASTER_DATA, SUPPORTED_INDEX_LIST, ANALYSIS_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.data_helper import save_csv, load_csv

import src.data.economy_loader as ecoloader
import src.data.economy_cleaner as ecocleaner
import src.data.exogenous_events_loader as evloder
import src.data.exogenous_events_cleaner as evcleaner
from src.data.schema import ECONOMY_MASTER_SCHEMA, UPDATES_MASTER_SCHEMA, METADATA_SCHEMA


    #===================
    #Helper Functions
    #===================
def create_metadata_file():
    """ creates a metadata file if one doesnt exist"""
    metadata = METADATA_SCHEMA
    return metadata

def load_metadata() -> dict:
    """loads the metadata.json file in data/metadata"""
    try:
        with open(METADATA_JSON, "r", encoding="utf-8") as file:
            metadata = json.load(file)
        return metadata
    except FileNotFoundError:
        metadata = create_metadata_file()
        print("a metadata file does not exist so one has been created")
        return metadata

def save_metadata(metadata) -> None:
    """saves the metadata.json file in data/metadata"""
    with open(METADATA_JSON, "w",encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)
        print("metadata successfully updated")

def update_metadata(update_type:str="all",economic_path:Path=ECONOMY_MASTER_DATA,events_path:Path=EVENTS_MASTER_DATA) -> dict | None:
    """  updates the metadata.json object based on the update type"""

    metadata = load_metadata()
    update_time = datetime.now().strftime("%Y-%m-%d")
    valid_update_types = ["all","economic","events"]

    economic_data = pd.read_csv(economic_path, index_col="date")
    economic_data.index = pd.to_datetime(economic_data.index)
    events_data = pd.read_csv(events_path, index_col="date")
    events_data.index = pd.to_datetime(events_data.index)

    if update_type == valid_update_types[0]:
        metadata = {
        "economic_data": {
                "last_updated": update_time,
                "earliest_date": economic_data["date"].min().strftime("%Y-%m-%d")
            },
            "event_data": {
                "last_updated": update_time,
                "earliest_date": events_data["date"].min().strftime("%Y-%m-%d"),
                "total_events": len(events_data)
            }
        }
    elif update_type == valid_update_types[1]:
        metadata["economic_data"]["last_updated"] = update_time
        if economic_data.empty or len(economic_data) == 0:
            metadata["economic_data"]["earliest_date"] = None
        else:
            metadata["economic_data"]["earliest_date"] = (economic_data.index.min().strftime("%Y-%m-%d"))
    elif update_type == valid_update_types[2]:
        metadata["event_data"]["last_updated"] = update_time
        if events_data.empty or len(events_data) == 0:
            metadata["economic_data"]["earliest_date"] = None
        else:
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
    METADATA_LAST_UPDATED_CPI= METADATA["economic_data"].get("last_updated")
    METADATA_LAST_UPDATED_EVENTS=METADATA["event_data"].get("last_updated")

    print(METADATA_LAST_UPDATED_EVENTS)

    today = datetime.now().date()
    if update_type == "economic":
        last_updated = METADATA_LAST_UPDATED_CPI
    elif update_type == "events":
        last_updated = METADATA_LAST_UPDATED_EVENTS
    else:
        return False

    print(f"data was last updated {last_updated}.")

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
def initialize_data():
    """ carries out a sequence of data updates should data not exist in the application"""

    update_economy = False
    update_events = False

    if load_csv("master",ANALYSIS_DATA_DIR,"date") is None:
        new_economic_master_file = pd.DataFrame(columns=ECONOMY_MASTER_SCHEMA)
        new_economic_master_file.set_index("date",inplace=True)
        save_csv("master", new_economic_master_file,ANALYSIS_DATA_DIR,True)
        update_economy = True


    if load_csv("events index",ANALYSIS_DATA_DIR,"date") is None:
        new_events_master_file = pd.DataFrame(columns=UPDATES_MASTER_SCHEMA)
        new_events_master_file.set_index("date",inplace=True)
        save_csv("events index",new_events_master_file,ANALYSIS_DATA_DIR,True)
        update_events = True

    if update_economy:
        update_economic_data()
        clean_economic_data()
    if update_events:
        data = evloder.initialise_events_data()
        if isinstance(data, pd.DataFrame):
            evloder.create_event_blacklist(data)
        clean_events_data(mode=False)

    return
    
def update_economic_data():
    """ carries out a sequence of functions to update CPI data
    stored in the data DIR
    """
    update_type = "economic"
    data_status = updated_needed(update_type)
    if not data_status:
        return "an update is not required, the data is too recent"

    refresh_attempt = ecoloader.refresh_cpi_data()
    if not refresh_attempt:
        return "there was an error updating the economic data."


    update_metadata(update_type)
    return f"Economic data successfully updated to {datetime.today()}."

def clean_economic_data() -> None:
    """ carries out a sequence of functions to clean the CPI data stored
    in the data DIR"""
    indices = ecocleaner.load_all_indices(SUPPORTED_INDEX_LIST)

    for index_name, dataframe in indices.items():
        dataframe = ecocleaner.clean_index(dataframe)
        dataframe = ecocleaner.convert_timestamp(dataframe)
        indices[index_name] = dataframe
        save_csv(index_name, dataframe, PROCESSED_DATA_DIR ,False)

    print("economic data cleaning successful.")

    indices = ecocleaner.merge_indices(indices)
    save_csv("master",indices,ANALYSIS_DATA_DIR,False)

    print("economic data mastering successful.")

    return

def update_events_data():
    """ carries out a sequence of functions to update exogenous events data
    """
    update_type = "events"
    data_status = updated_needed(update_type)
    if not data_status:
        print("an update is not required, the data is too recent.")
        return False

    refresh_attempt = evloder.contact_wiki_for_updates()
    dated_refresh_attempt = evloder.contact_wiki_for_dates()
    update_metadata(update_type)

    print(f"Exogenous Events update process completed: {datetime.today()}.")
    return True

def clean_events_data(mode=True):
    """ carried out a sequence of functions to clean the updates data stored
    in the data DIR"""
    #check the blacklisted events have been removed before going further
    evcleaner.blacklist_check()
    evcleaner.classify_events(mode)
    evcleaner.create_event_index()
    return
